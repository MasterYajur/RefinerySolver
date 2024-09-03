#where functions for creating constraints and vars
#model.solver needs to be a parameter and names should start with id of ref
#create variables and constraints
def create_variables(ref, model):
    vars = set(

    for unit in ref.units:
        for var in ref.units[unit]["inputs"]+ref.units[unit]["outputs"]:
            vars.add(var)

    for var in vars:
        model.variables[ref.name + "_" +var] = model.solver.NumVar(0, model.solver.infinity(), ref.name + "_" + var)

    #print(model.solver.NumVariables())


def make_cap_constraints(ref, model):
    #constraint for crude capacity
    for crude in ref.crudes:
        constraint  = model.solver.Constraint(0, ref.crudes[crude])
        constraint.SetCoefficient(model.variables[ref.name + "_" +crude],1)

    for unit in ref.units:
        if "capacity" in ref.units[unit].keys():
            constraint = model.solver.Constraint(0, ref.units[unit]["capacity"])
            for inp in ref.units[unit]["inputs"]:
                constraint.SetCoefficient(model.variables[ref.name + "_" +inp],1)



    model.solver.Add(model.variables[ref.name + "_" +"LuO"] <= ref.LuO_upper)
    
    model.solver.Add(model.variables[ref.name + "_" +"LuO"] >= ref.LuO_lower)
    model.solver.Add(model.variables[ref.name + "_" +"PG"] >= ref.pg_to_rg*model.variables[ref.name + "_" +"RG"])


def make_distillation_constraints(ref, model):

    for intermediate in ref.intermediate_products:
        constraint = model.solver.Constraint(0,0)

        constraint.SetCoefficient(model.variables[ref.name + "_" +intermediate],-1)

        for crude in ref.crudes:
            constraint.SetCoefficient(model.variables[ref.name + "_" +crude],ref.CDU_split[crude][intermediate])


def make_balancing_constraints(ref, model): 
#yield:
    model.solver.Add(model.variables[ref.name + "_" + "LO"] == model.variables[ref.name + "_" +"LOC"] + model.variables[ref.name + "_" +"LOJF"] + 0.55*model.variables[ref.name + "_" +"FO"])
    model.solver.Add(model.variables[ref.name + "_" +"HO"] == model.variables[ref.name + "_" +"HOC"] + model.variables[ref.name + "_" +"HOJF"] + 0.17*model.variables[ref.name + "_" +"FO"])
    model.solver.Add(model.variables[ref.name + "_" +"JF"] == model.variables[ref.name + "_" +"LOJF"] + model.variables[ref.name + "_" +"HOJF"] + model.variables[ref.name + "_" +"COJF"] + model.variables[ref.name + "_" +"RJF"])


#mass conservation:
    model.solver.Add(model.variables[ref.name + "_" +"LN"] == model.variables[ref.name + "_" +"LNPG"] + model.variables[ref.name + "_" +"LNRG"] + model.variables[ref.name + "_" +"LNR"])
    model.solver.Add(model.variables[ref.name + "_" +"MN"] == model.variables[ref.name + "_" +"MNPG"] + model.variables[ref.name + "_" +"MNRG"] + model.variables[ref.name + "_" +"MNR"])
    model.solver.Add(model.variables[ref.name + "_" +"HN"] == model.variables[ref.name + "_" +"HNPG"] + model.variables[ref.name + "_" +"HNRG"] + model.variables[ref.name + "_" +"HNR"])

    model.solver.Add(model.variables[ref.name + "_" +"CO"] == model.variables[ref.name + "_" +"COJF"] + 0.22*model.variables[ref.name + "_" +"FO"])



    model.solver.Add(model.variables[ref.name + "_" +"R"] == model.variables[ref.name + "_" +"RJF"] + model.variables[ref.name + "_" +"RLuO"] + 0.0555*model.variables[ref.name + "_" +"FO"] )

    model.solver.Add(model.variables[ref.name + "_" +"ReG"] == model.variables[ref.name + "_" +"RGPG"] + model.variables[ref.name + "_" +"RGRG"])
    model.solver.Add(model.variables[ref.name + "_" +"CG"] == model.variables[ref.name + "_" +"CGPG"] + model.variables[ref.name + "_" +"CGRG"])

    model.solver.Add(model.variables[ref.name + "_" +"PG"] == model.variables[ref.name + "_" +"LNPG"] + model.variables[ref.name + "_" +"MNPG"] + model.variables[ref.name + "_" +"HNPG"] + model.variables[ref.name + "_" +"RGPG"] + model.variables[ref.name + "_" +"CGPG"])
    model.solver.Add(model.variables[ref.name + "_" +"RG"] == model.variables[ref.name + "_" +"LNRG"] + model.variables[ref.name + "_" +"MNRG"] + model.variables[ref.name + "_" +"HNRG"] + model.variables[ref.name + "_" +"RGRG"] + model.variables[ref.name + "_" +"CGRG"])



def make_reforming_balance(ref, model):
    for product in ref.reforming_split:
        constraint = model.solver.Constraint(0,0)

        constraint.SetCoefficient(model.variables[ref.name + "_" +product],-1)

        for itm in ref.reforming_split[product]:
            constraint.SetCoefficient(model.variables[ref.name + "_" +itm], ref.reforming_split[product][itm])



def cracking_balance(ref, model):
    for product in ref.cracking_split:
        constraint = model.solver.Constraint(0,0)

        constraint.SetCoefficient(model.variables[ref.name + "_" +product],-1)

        for itm in ref.cracking_split[product]:
            constraint.SetCoefficient(model.variables[ref.name + "_" +itm], ref.cracking_split[product][itm])

            
def coking_balance(ref, model):
    for product in ref.coking_split:
        constraint = model.solver.Constraint(0,0)

        constraint.SetCoefficient(model.variables[ref.name + "_" +product],-1)

        for itm in ref.coking_split[product]:
            constraint.SetCoefficient(model.variables[ref.name + "_" +itm], ref.coking_split[product][itm])

def octane_tolerence(ref, model):
    model.solver.Add(90*model.variables[ref.name + "_" +"LNPG"] + 80*model.variables[ref.name + "_" +"MNPG"] + 70*model.variables[ref.name + "_" + "HNPG"] + 115*model.variables[ref.name + "_" +"RGPG"] + 105*model.variables[ref.name + "_" +"CGPG"] >= 94*model.variables[ref.name + "_" +"PG"])
    model.solver.Add(90*model.variables[ref.name + "_" +"LNRG"] + 80*model.variables[ref.name + "_" +"MNRG"] + 70*model.variables[ref.name + "_" +"HNRG"] + 115*model.variables[ref.name + "_" +"RGRG"] + 105*model.variables[ref.name + "_" +"CGRG"] >= 84*model.variables[ref.name + "_" +"RG"])


def vapour_pressure(ref, model):
    model.solver.Add(model.variables[ref.name + "_" +"JF"] >= model.variables[ref.name + "_" +"LOJF"] + 0.6*model.variables[ref.name + "_" +"HOJF"] + 1.5*model.variables[ref.name + "_" +"COJF"] + 0.05*model.variables[ref.name + "_" +"RJF"])



def create_model(ref, model):
    

    create_variables(ref, model)

    make_cap_constraints(ref, model)

    make_reforming_balance(ref, model)

    make_balancing_constraints(ref, model)

    make_distillation_constraints(ref, model)

    cracking_balance(ref, model)

    coking_balance(ref, model)
    
    octane_tolerence(ref, model)

    vapour_pressure(ref, model)



