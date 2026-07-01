from cobaya import run
from cobaya.log import LoggedError
from cobaya.yaml import yaml_load_file
from mpi4py import MPI
import sys

''' 
    More general version of the MPI code MPI_implementation. can be used for any config file and any number of chains. 
    The path to the config file must be given as argument when executing.
    Execution : mpiexec -n 4 python MPI_general.py path/to/config.yaml (need to activate the right env before)
    Add flag force, -f or -force to force the run even if output already exists.
'''
def main():
    want_force = False # Set to True to force the run even if output already exists

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        config = yaml_load_file(config_file)

    else:
        yaml_file = '/home/adrien/PDM/code/PDM2026_wsl/yaml_config/w_wa.yaml' #load yaml config file for LCDM
        # path = '/home/adrien/PDM/code/PDM2026_wsl/notebooks/fisher_forecast/DESI2_fullsky/DESI2_fullsky_mean.txt'  
        config = yaml_load_file(yaml_file)

        # config['likelihood']['bao.desi_dr2']['measurements_file'] = path
        print(config['likelihood']['bao.desi_dr2']['measurements_file'])

        # config['output'] = "cobaya_test_runs/base_w_wa/LCDM_fakedata_not_random_1"
        # config['sampler']['mcmc']['Rminus1_stop'] = 0.01
        # config['sampler']['mcmc']['covmat'] = "cobaya_test_runs/base_LCDM/LCDM_fakedata_not_random_MPItest8.covmat"
        # config['params']['omch2']['ref'] = 0.125 # Om=0.3, h=0.7 then Oc = Om-Ob = 0.3-0.045 = 0.255, so Oc*h^2 = 0.25*0.7^2 = 0.125

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    print(f"Rank {rank} running")

    # if rank == 0:
    #     print("Running with config file:", config_file)
    #     print("Output directory:", config['output'])
    #     print("Force run:", want_force)
    #     # print(config['likelihood']['bao.desi_dr2']['measurements_file'])


    # print("File exists:", os.path.exists(path))
    # print("Absolute path:", os.path.abspath(path))

    if len(sys.argv) > 2:
        want_force = (sys.argv[2].lower() == "-force") or (sys.argv[2].lower() == "--force") or (sys.argv[2].lower() == "force") or (sys.argv[2].lower() == "-f") or (sys.argv[2].lower() == "--f")

    success = False
    try:
        upd_info, mcmc = run(config, force=want_force)
        success = True
    except LoggedError as err:
        print(rank, err)
        pass

    # Did it work? (e.g. did not get stuck)
    success = all(comm.allgather(success))

    if not success and rank == 0:
        print("Sampling failed!")

if __name__ == "__main__":    
    main()