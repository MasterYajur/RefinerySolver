	#contains schema for ref data
class Refinery:
	def __init__(self, name):
		self.name = name

		self.crudes = {"A":20000, "B":30000}
		self.LuO_upper = 1000
		self.LuO_lower = 500
		self.CDU_split = {
			"A" : {
				"LN" : 0.15,
				"MN" : 0.15,
				"HN" : 0.17,
				"LO" : 0.15,
				"HO" : 0.23,
				"R" : 0.1
			},
			"B" : {
				"LN" : 0.2,
				"MN" : 0.2,
				"HN" : 0.18,
				"LO" : 0.08,
				"HO" : 0.16,
				"R" : 0.15
			}

		}
		self.reforming_split = {
			"ReG" :{
				"LNR" : 0.6,
				"MNR" : 0.52,
				"HNR" : 0.45
			}
		}
		self.cracking_split = {
			"CG" : {
				"LOC" : 0.28,
				"HOC" : 0.2
			},
			"CO" : {
				"LOC" : 0.68,
				"HOC" : 0.75
			}
		}
		self.coking_split = {
			"LuO" : {
				"RLuO" : 0.5
			}
		}
		self.MDB_recipe = {
			"FO" :{
				"CO" : 3/18,
				"LOB" : 10/18,
				"HOB" : 4/18,
				"RB" : 1/18
			}
		}
		self.pg_to_rg  = 0.4

		self.octane_value = {
			"LN" : 70,
			"MN" : 80,
			"HN" : 90,
			"ReG" : 115,
			"CG" : 105,
			"RG" : 84,
			"PG" : 94
		}


		self.vapor_pressure = {
			"LO" : 1,
			"HO" : 0.6,
			"CO" : 1.5,
			"R" : 0.105

		}

		self.intermediate_products = ["LN", "MN", "HN", "LO", "HO", "R"]
		self.final_products = ["PG", "RG", "JF",  "FO", "LuO"]
		self.units = {
			"CDU":{
				"inputs": ["A","B"],
				"outputs": self.intermediate_products,
				"capacity" : 45000
			},
			"Reforming" : {
				"inputs" : [
					"LNR",
					"MNR",
					"HNR"
				],
				"outputs":[
					"ReG"
				],
				"capacity" : 10000


			},
			"Cracking" : {
				"inputs" : [
					"LOC",
					"HOC"
				],
				"outputs":[
					"CG",
					"CO"
				],
				"capacity" : 8000

			},
			"Coking" : {
				"inputs" : [
					"RLuO"
				],
				"outputs":[
					"LuO"
				]

			},
			"LDB" : {
				"inputs" : [
					"LNPG",
					"LNRG",
					"MNPG",
					"MNRG",
					"HNPG",
					"HNRG",
					"RGPG",
					"RGRG",
					"CGPG",
					"CGRG"
				],
				"outputs":[
					"PG",
					"RG"
				]

			},
			"MDB" : {
				"inputs" : [
					"LOJF",
					"HOJF",
					"COJF",
					"RJF",
					"RLuO"
				],

				"outputs":[
					"JF",
					"FO",
					"LuO"
				]

			}
		}


