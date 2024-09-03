#solver class containing a varaible dict and a function solve which will call the or-tool solver
#solver is the object which contains the main LP modle where we add our main objective function
from ortools.linear_solver import pywraplp
from ortools.init.python import init


class Ref_Solver():
	def __init__(self):
		self.variables = {}
		self.final_products = ["PG", "RG", "JF",  "FO", "LuO"]
		self.profits = {"PG": 100,"RG" :80,"JF": 75, "FO" : 20,"LuO": 10}
		self.solver = pywraplp.Solver.CreateSolver("GLOP")
		self.production = []
		self.status = None


	def export_lp_model(self):
		lp_filepath = "model.lp"
		with open(lp_filepath, mode="w") as f:
			f.write(self.solver.ExportModelAsLpFormat(False))


	def solve(self, refs, num, demands, ref_num, Days, pmodel = None):
		#add a coupling constraint sum of the jet fuel should be less than some finite quantity test and see and plot the production for each ref 
		self.couple(refs, demands, ref_num, Days)
		obj = None
		M = 0
		if num == 1:
			self.minimize_demands(refs, demands) #to set constraints and obj for minimizing demand difference mode

		if num == 2:
			self.balance_load_avg(refs, demands, ref_num, Days, pmodel)
			#self.balance_load_avg(refs, demands)


		if num == 3:
			self.maximize_profits(refs, demands, ref_num, Days, pmodel)



		self.export_lp_model()

		self.status = self.solver.Solve()

		if self.status == pywraplp.Solver.OPTIMAL:
			return True 		
		else:
			return False



	def couple(self, refs, demands, ref_num, Days): 
		for product in self.final_products:
			self.variables[product] =  self.solver.NumVar(0, self.solver.infinity(), product)

			constraint = self.solver.Constraint(0,0)

			constraint.SetCoefficient(self.variables[product],-1)
		

			for ref in refs:
				constraint.SetCoefficient(self.variables[ref.name + "_" + product], 1)


		for product in self.final_products:
			for i in range(1, ref_num + 1):
				pname = str(i) + "_" + product
				self.variables[pname] = self.solver.NumVar(0, self.solver.infinity(), pname)
				constraint = self.solver.Constraint(0,0)
				constraint.SetCoefficient(self.variables[pname], -1)

				for d in range(1, Days+1):
					constraint.SetCoefficient(self.variables[str(i) + "_day_" + str(d) + "_" + product], 1)
				#now "1_FO" stores total fuel production by FO

		
	def minimize_demands(self, refs, demands):
		#add constraints
		for product in self.final_products:
			self.variables["abs_" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_"+product)

			self.variables["abs_P" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_P"+product)


			self.solver.Add(self.variables["abs_"+product] == self.variables[product] - demands[product])

			self.solver.Add(self.variables["abs_"+product] <= self.variables["abs_P"+product])
			self.solver.Add(self.variables["abs_"+product] >= -1*self.variables["abs_P"+product])



		obj = sum([self.variables["abs_P" + product] for product in self.final_products])
		self.solver.Minimize(obj)



	def minimize_demands_coeff(self, refs, demands, ref_num, Days, pmodel):
		#add constraints
		for product in self.final_products:
			self.variables["abs_" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_"+product)

			self.variables["abs_P" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_P"+product)


			self.solver.Add(self.variables["abs_"+product] == self.variables[product] - demands[product])

			self.solver.Add(self.variables["abs_"+product] <= self.variables["abs_P"+product])
			self.solver.Add(self.variables["abs_"+product] >= -1*self.variables["abs_P"+product])



		obj = sum([self.profit[product]*self.variables["abs_P" + product] for product in self.final_products])
		self.solver.Minimize(obj)








	def balance_load_avg(self, refs, demands, ref_num, Days, pmodel):

		#first balance between all refineries [FO_ref1 and FO_ref2 ]

		#then balance between all days for each ref

		#final production is now definitely met
		for product in self.final_products:
			self.solver.Add(self.variables[product] >= demands[product])

		#now balance the loads, for that for each pro introduce two variablea and so on


		for product in self.final_products:
			tot_prod = 0
			for i in range(1, ref_num+1):
				tot_prod += pmodel.variables[str(i) + "_" + product].solution_value()

			avg_prod = tot_prod/ref_num

			for i in range(1, ref_num+1):

				self.variables["abs_" + str(i) + "_" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_" + str(i) + "_" + product)
				self.variables["abs_P" + str(i) + "_" + product] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "abs_P" + str(i) + "_" + product)


				self.solver.Add(self.variables["abs_" + str(i) + "_" + product] == self.variables[str(i) + "_" + product] - avg_prod)


				self.solver.Add(self.variables["abs_" + str(i) + "_" + product] <= self.variables["abs_P" + str(i) + "_" + product])
				self.solver.Add(self.variables["abs_" + str(i) + "_" + product] >= -1*self.variables["abs_P" + str(i) + "_" + product])



		obj = sum([self.variables["abs_P" + str(i) + "_" + product] for i in range(1, ref_num+1) for product in self.final_products])
		self.solver.Minimize(obj)



			#now we will try to minimize the difference between each ref production and avg value


	def balance_load_avg_days(self, refs, demands, ref_num, Days, pmodel):
		for product in self.final_products:
			self.solver.Add(self.variables[product] >= demands[product])

		#now production of each refinery should at least be as it was before

		for product in self.final_products:
			for i in range(1, ref_num+1):
				self.solver.Add(self.variables[str(i) + "_" + product] >= pmodel.variables[str(i) + "_" + product].solution_value())

		#now we really need to balance loads across each day for a ref
		obj = 0  
		for product in self.final_products:

			for i in range(1, ref_num+1):
				tot = pmodel.variables[str(i) + "_" + product].solution_value()
				avg_prod = tot/Days
				for day in range(1, Days+1):
					varn = "abs_" + str(i) + "_day_" + str(day) + "_" + product
					self.variables[varn] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), varn)
					self.variables["P"+varn] = self.solver.NumVar(-self.solver.infinity(), self.solver.infinity(), "P"+varn)


					self.solver.Add(self.variables[varn] == self.variables[varn[4:]] - avg_prod)


					self.solver.Add(self.variables[varn] <= self.variables["P"+varn])
					self.solver.Add(self.variables[varn] >= -1*self.variables["P"+varn])
					obj += self.variables["P"+varn]
		self.solver.Minimize(obj)



	def maximize_profits(self, refs, demands, ref_num, Days, pmodel):

		for product in self.final_products:
			self.solver.Add(self.variables[product] >= demands[product])

		#now production of each refinery should at least be as it was before

		for product in self.final_products:
			for i in range(1, ref_num+1):
				self.solver.Add(self.variables[str(i) + "_" + product] >= pmodel.variables[str(i) + "_" + product].solution_value())
				
		obj = sum([self.variables[product]*self.profits[product] for product in self.final_products])
		self.solver.Maximize(obj)


















