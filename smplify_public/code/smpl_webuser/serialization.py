'''
Copyright 2015 Matthew Loper, Naureen Mahmood and the Max Planck Gesellschaft.  All rights reserved.
This software is provided for research purposes only.
By using this software you agree to the terms of the SMPL Model license here http://smpl.is.tue.mpg.de/license

More information about SMPL is available here http://smpl.is.tue.mpg.
For comments or questions, please email us at: smpl@tuebingen.mpg.de


About this file:
================
This file defines the serialization functions of the SMPL model. 

Modules included:
- save_model:
  saves the SMPL model to a given file location as a .pkl file
- load_model:
  loads the SMPL model from a given file location (i.e. a .pkl file location), 
  or a dictionary object.

'''

__all__ = ['load_model', 'save_model']

import numpy as np
import cPickle as pickle
import chumpy as ch
from chumpy.ch import MatVecMult
from posemapper import posemap
from verts import verts_core, verts_decorated
    
def save_model(model, fname):
    m0 = model
    trainer_dict = {'v_template': np.asarray(m0.v_template),'J': np.asarray(m0.J),'weights': np.asarray(m0.weights),'kintree_table': m0.kintree_table,'f': m0.f, 'bs_type': m0.bs_type, 'posedirs': np.asarray(m0.posedirs)}    
    if hasattr(model, 'J_regressor'):
        trainer_dict['J_regressor'] = m0.J_regressor
    if hasattr(model, 'J_regressor_prior'):
        trainer_dict['J_regressor_prior'] = m0.J_regressor_prior
    if hasattr(model, 'weights_prior'):
        trainer_dict['weights_prior'] = m0.weights_prior
    if hasattr(model, 'shapedirs'):
        trainer_dict['shapedirs'] = m0.shapedirs
    if hasattr(model, 'vert_sym_idxs'):
        trainer_dict['vert_sym_idxs'] = m0.vert_sym_idxs
    if hasattr(model, 'bs_style'):
        trainer_dict['bs_style'] = model.bs_style
    else:
        trainer_dict['bs_style'] = 'lbs'
    pickle.dump(trainer_dict, open(fname, 'w'), -1)


def backwards_compatibility_replacements(dd):

    # replacements
    if 'default_v' in dd:
        dd['v_template'] = dd['default_v']
        del dd['default_v']
    if 'template_v' in dd:
        dd['v_template'] = dd['template_v']
        del dd['template_v']
    if 'joint_regressor' in dd:
        dd['J_regressor'] = dd['joint_regressor']
        del dd['joint_regressor']
    if 'blendshapes' in dd:
        dd['posedirs'] = dd['blendshapes']
        del dd['blendshapes']
    if 'J' not in dd:
        dd['J'] = dd['joints']
        del dd['joints']

    # defaults
    if 'bs_style' not in dd:
        dd['bs_style'] = 'lbs'



def ready_arguments(fname_or_dict):

    if not isinstance(fname_or_dict, dict):
        dd = pickle.load(open(fname_or_dict))
    else:
        dd = fname_or_dict
        
    backwards_compatibility_replacements(dd)
        
    want_shapemodel = 'shapedirs' in dd
    nposeparms = dd['kintree_table'].shape[1]*3

    if 'trans' not in dd:
        dd['trans'] = np.zeros(3)
    if 'pose' not in dd:
        dd['pose'] = np.zeros(nposeparms)
    if 'shapedirs' in dd and 'betas' not in dd:
        dd['betas'] = np.zeros(dd['shapedirs'].shape[-1])

    for s in ['v_template', 'weights', 'posedirs', 'pose', 'trans', 'shapedirs', 'betas', 'J']:
        if (s in dd) and not hasattr(dd[s], 'dterms'):
            dd[s] = ch.array(dd[s])

    want_shapemodel = False
    if want_shapemodel:
        #dd['betas'][0] = 10

        dd['v_shaped'] = dd['shapedirs'].dot(dd['betas'])+dd['v_template']
        v_shaped = dd['v_shaped']
        J_tmpx = MatVecMult(dd['J_regressor'], v_shaped[:,0])        
        J_tmpy = MatVecMult(dd['J_regressor'], v_shaped[:,1])        
        J_tmpz = MatVecMult(dd['J_regressor'], v_shaped[:,2])        
        dd['J'] = ch.vstack((J_tmpx, J_tmpy, J_tmpz)).T    
        dd['v_posed'] = v_shaped + dd['posedirs'].dot(posemap(dd['bs_type'])(dd['pose']))

        print "*******"
        print "Betas : " + str(dd['betas'].shape)
        print "v_template : " + str(dd['v_template'].shape)
        print "shapedirs : " + str(dd['shapedirs'].shape)
        print "v_shaped : " + str(dd['v_shaped'].shape)

        print dd['betas']

    else:    
        dd['v_posed'] = dd['v_template'] + dd['posedirs'].dot(posemap(dd['bs_type'])(dd['pose']))
            
    return dd

def save_model_json(fname_or_dict):
    dd = ready_arguments(fname_or_dict)
    import json
    from json import encoder
    encoder.FLOAT_REPR = lambda o: format(o, '.5f')
    customDict = dict()
    for k, v in dd.items():
        #print "KEY: " + k
        #print "TYPE: " + v.__class__.__name__

        if k == "J_regressor_prior":
            pass
            #print "\t" + str(v.shape)
            # No save
        if k == "pose":
            #print "\t" + str(v.shape)
            tmp = np.array(v)
            tmp = tmp.reshape(24,3)
            customDict[k] = tmp.tolist()
        if k == "f":
            #print "\t" + str(v.shape)
            customDict[k] = (np.array(v)).tolist()
            #print v
        if k == "J_regressor":
            data = np.zeros(shape=(0,3))
            data = np.vstack((data,np.array([1,2,3])))
            rows, cols = v.shape
            for r in range(0,rows):
                for c in range(0,cols):
                    d = v[r,c]
                    if d != 0.0:
                        print c
                        data = np.vstack((data,np.array([r,c,d])))
            print data.shape
            customDict[k] = data.tolist()
            # No save
        if k == "betas":
            customDict[k] = (np.array(v)).tolist()
            #print "\t" + str(v.shape)
            #print v
            # No save
        if k == "kintree_table":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "J":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "v_shaped":
            pass
            #print "\t" + str(v.shape)
            #print v
            # No save
        if k == "weights_prior":
            pass
            #print "\t" + str(v.shape)
            #print v
            # No save
        if k == "trans":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "v_posed":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "weights":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "vert_sym_idxs":
            #print "\t" + str(v.shape)
            #print v
            customDict[k] = (np.array(v)).tolist()
        if k == "posedirs":
            #customDict[k] = (np.array(v)).tolist()
            pass
            #print "\t" + str(v.shape)
            # print v
            # No save
        if k == "pose_training_info":
            #print v
            customDict[k] = v
        if k == "bs_style":
            #print v
            customDict[k] = v
        if k == "v_template":
            pass
            #print "\t" + str(v.shape)
            #print v
            # No save
        if k == "shapedirs":
            customDict[k] = (np.array(v)).tolist()
            pass
            #print "\t" + str(v.shape)
            # print v
            # No save
        if k == "bs_type":
            #print v
            customDict[k] = (np.array(v)).tolist()
    #with open("/home/ryaadhav/smpl_cpp/male_model.json", 'w') as outfile:
    #    json.dump(customDict, outfile)

tmp = 0
def load_model(fname_or_dict, params = None):
    dd = ready_arguments(fname_or_dict)

    #save_model_json(fname_or_dict)
    #stop

    #dd['pose'][5] = 0.78

    args = {
        'pose': dd['pose'],
        'v': dd['v_posed'],
        'J': dd['J'],
        'weights': dd['weights'],
        'kintree_table': dd['kintree_table'],
        'xp': ch,
        'want_Jtr': True,
        'bs_style': dd['bs_style'],
    }

    #global tmp
    #tmp+=0.5
    #print tmp
    dd['betas'][3] = 20

    args2 = {
        'trans': dd['trans'],
        'pose': dd['pose'],
        'v_template': dd['v_template'],
        'J': dd['J_regressor'],
        'weights': dd['weights'],
        'kintree_table': dd['kintree_table'],
        'bs_style': dd['bs_style'],
        'f': dd['f'],
        'bs_type': dd['bs_type'],
        'posedirs': dd['posedirs'],
        'betas' : dd['betas'],
        'shapedirs' : dd['shapedirs'],
        'want_Jtr': True
    }

    # FOR SHAPE
    return verts_decorated(**args2)

    # pose, v, J, weights, kintree_table, want_Jtr, xp
    result, Jtr = verts_core(**args)
    result = result + dd['trans'].reshape((1,3))
    result.J_transformed = Jtr + dd['trans'].reshape((1,3))

    #print result.J_transformed.shape

    for k, v in dd.items():
        setattr(result, k, v)

    return result

