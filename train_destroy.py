import argparse
import math

import pytorch_lightning as pl

from nlns.models.res_gated_gcn import ResGatedGCN
from nlns.models.dataloader import DataModule

def n_customers(s):
  if "," not in s:
    return int(s)
  else:
    try:
      m, M = map(int, s.split(','))
      return m, M
    except:
      raise argparse.ArgumentTypeError("Number of customers must be in format <min>,<max> if randomly sampled num of customers is used.")

parser = argparse.ArgumentParser(description='Train neural destroy operator')
parser.add_argument('-o', '--out', type=str, required=True)
parser.add_argument('-n', '--n_customers', type=n_customers, required=True)
parser.add_argument('-t', '--train', type=int, required=True)
parser.add_argument('-v', '--valid', type=int, required=True)
parser.add_argument('-b', '--batch-size', type=int, required=True)
parser.add_argument('--seed', type=int, required=False, default=42)
parser.add_argument('--distribution', type=str, required=False, default="nazari")
parser.add_argument('--log-interval', type=int, required=False, default=10)
parser.add_argument('--valid-interval', type=int, required=False, default=50)
parser.add_argument('--num-neighbors', type=int, required=False, default=20)
parser.add_argument('--max-steps', type=int, required=False)

args = parser.parse_args()

if __name__ == "__main__":
  data = DataModule(num_nodes=args.n_customers,
                    valid_instances=args.valid,
                    batch_size=args.batch_size,
                    num_neighbors=args.num_neighbors)
  
  # following Joshi (2019) and Kool (2022) we train for at most 1500
  # epochs with 500 steps for each epoch.
  max_steps = args.max_steps if hasattr(args, "max_steps") else (args.batch_size * 500) * 1500
  
  destroy = ResGatedGCN(num_neighbors=args.num_neighbors)
  wandb_logger = pl.loggers.WandbLogger(project="NeuRouting")
 
  trainer = pl.Trainer(max_epochs=None,
                       max_steps=max_steps,
                       logger=wandb_logger,
                       log_every_n_steps=args.log_interval,
                       val_check_interval=args.valid_interval,
                       callbacks=[
                         pl.callbacks.StochasticWeightAveraging(swa_lrs=1e-2),
                         pl.callbacks.EarlyStopping(monitor="valid/loss", patience=2)
                       ])
  
  #trainer.fit(destroy, datamodule=data)
    