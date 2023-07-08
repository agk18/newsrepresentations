
import data_loader  # new
import models  # new
import losses # new
import traintest #new

import pandas as pd
import numpy as np
import torch.nn as nn
import datetime


if __name__=='__main__':


    cutoff = datetime.datetime.strptime('2004-01-01', '%Y-%m-%d')


    pd_X = pd.read_csv('sample_data_X.csv',index_col='DATE' )
    pd_y = pd.read_csv('sample_data_y.csv',index_col='DATE' )
    pd_X.index = pd.to_datetime(pd_X.index,format='%Y-%m-%d')
    for c in pd_X.columns:
        pd_X[c] = pd_X[c].astype(np.float32)
    pd_y.index = pd.to_datetime(pd_y.index,format='%Y-%m-%d')
    X_names_in = pd_X.columns
    Y_names_in = pd_y.columns


    train_loader, test_loader, train_data, test_data = data_loader.load_sent_data( train_batch_size = 50,
                                                            test_batch_size = 1000,
                                                            df = pd_X.join(pd_y), df_cutoff = cutoff,
                                                            Y_names=Y_names_in, Y_name_types={y:int for y in Y_names_in }, # int},
                                                            X_names=X_names_in,
                                                            train_dates=pd.date_range(start=cutoff, end="2018-06-30"),
                                                            convert_Y_to_labels = True, shuffle = True )

    # set up
    saemodel = models.encoder_decoder( X_dim_in=len(X_names_in), map_layer_dims=[10], encoding_layer_dim=len(Y_names_in),
                                                 dropout_p=0.1, classification=True,  external_enc = None )

    # set up train / test
    sae = traintest.sae(model_in = saemodel,loss_fct_in = losses.loss_fixedW,
                       sub_losses_in = [nn.MSELoss()]+ [nn.CrossEntropyLoss()]*len(Y_names_in), train_loss_wgt=False,
                       lr_in= 0.005,
                       sub_losses_in_wgt_init = [10 / len(Y_names_in)] + [0.05 / len(Y_names_in)] * (len(Y_names_in) ),
                       classification=True, firsttrain_reconstruction=10,  l2strength = 0.00001,
                       sparse_regularizer= 0.0)

    # train
    sae.train(epochs=40, train_loader = train_loader)
