

def check_sim_config(sim_config):
    count = 0
    for s in sim_config:
        if sim_config[s] == True:
            count += 1
    if count > 1:
        raise ValueError("Too many SIM_CONFIGs are True")
    elif count == 0:
        raise ValueError("No simulation selected as True")
