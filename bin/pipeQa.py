#!/usr/bin/env python
#
# Original filename: bin/pipeQa.py
#
# Author: 
# Email: 
# Date: Mon 2011-04-11 13:11:01
# 
# Summary: 
# 
"""
%prog [options] dataset
  dataset = Directory in TESTBED_PATH, full path to data, or database name
"""

import sys
import re
import optparse
import os
import datetime
import traceback
import copy
import time

import lsst.testing.pipeQA as pipeQA
import lsst.testing.pipeQA.analysis     as qaAnalysis
import lsst.pex.policy as pexPolicy
from lsst.pex.logging import Trace

import numpy

def mem(size="rss"):
    """Generalization; memory sizes: rss, rsz, vsz."""
    return int(os.popen('ps -p %d -o %s | tail -1' % (os.getpid(), size)).read())



#############################################################
#
# Main body of code
#
#############################################################

def main(dataset, dataIdInput, rerun=None, testRegex=".*", camera=None, exceptExit=False):

    if exceptExit:
        numpy.seterr(all="raise")


    ###  Get the data retrieval object  ###
    data = pipeQA.makeQaData(dataset, rerun=rerun, retrievalType=camera)


    ################################################
    # validate the dataId
    ################################################

    # allow LSST users to refer to LSST 'sensor' as 'ccd', just rename it accordingly
    if data.cameraInfo.name == 'lsstSim' and dataIdInput.has_key('ccd'):
        dataIdInput['sensor'] = dataIdInput['ccd']
        del dataIdInput['ccd']

    # make sure the dataId isn't polluted
    # take what we need for this camera, ignore the rest
    dataId = {}
    for name in data.dataIdNames:
        if dataIdInput.has_key(name):
            dataId[name] = dataIdInput[name]

    # if they requested a key that doesn't exist for this camera ... throw
    for k, v in dataIdInput.items():
        if (not k in data.dataIdNames) and (v != '.*'):
            raise Exception("Key "+k+" not available for this dataset (camera="+data.cameraInfo.name+")")




    #################################################
    #
    # Policy handling
    #
    #################################################
    
    # Policy for which plots to make and value of quality metrics
    policyDictName = "PipeQa.paf"
    policyFile = pexPolicy.DefaultPolicyFile("testing_pipeQA", policyDictName, "policy")
    policy  = pexPolicy.Policy.createPolicy(policyFile, policyFile.getRepositoryPath(), True)


    # multi-epoch policies
    multiEpochAnalysisList = []
    if data.cameraInfo.name in policy.getStringArray("doMultiEpochAstrom"):
        multiEpochAnalysisList.append(qaAnalysis.MultiEpochAstrometryQa())


    # single-epoch policies
    singleEpochAnalysisList = []
    if data.cameraInfo.name in policy.getStringArray("doZptQa"):
        zptMin = policy.get("zptQaMetricMin")
        zptMax = policy.get("zptQaMetricMax")
        singleEpochAnalysisList.append(qaAnalysis.ZeropointQaAnalysis(zptMin, zptMax))
    if data.cameraInfo.name in policy.getStringArray("doZptFitQa"):
        offsetMin = policy.get("zptFitQaOffsetMin")
        offsetMax = policy.get("zptFitQaOffsetMax")
        singleEpochAnalysisList.append(qaAnalysis.ZeropointFitQa(offsetMin, offsetMax))
    if data.cameraInfo.name in policy.getStringArray("doEmptySectorQa"):
        maxMissing = policy.get("emptySectorMaxMissing")
        singleEpochAnalysisList.append(qaAnalysis.EmptySectorQaAnalysis(maxMissing, nx = 4, ny = 4))
    if data.cameraInfo.name in policy.getStringArray("doAstromQa"):
        singleEpochAnalysisList.append(qaAnalysis.AstrometricErrorQaAnalysis(policy.get("astromQaMaxErr")))
    if data.cameraInfo.name in policy.getStringArray("doPhotCompareQa"):
        magCut   = policy.get("photCompareMagCut")
        deltaMin = policy.get("photCompareDeltaMin")
        deltaMax = policy.get("photCompareDeltaMax")
        rmsMax   = policy.get("photCompareRmsMax")
        slopeMin = policy.get("photCompareSlopeMinSigma")
        slopeMax = policy.get("photCompareSlopeMaxSigma")
        for types in policy.getStringArray("photCompareTypes"):
            cmp1, cmp2 = types.split()
            singleEpochAnalysisList.append(qaAnalysis.PhotCompareQaAnalysis(cmp1, cmp2, magCut, deltaMin, deltaMax,
                                                                 rmsMax, slopeMin, slopeMax))
    if data.cameraInfo.name in policy.getStringArray("doPsfShapeQa"):
        singleEpochAnalysisList.append(qaAnalysis.PsfShapeQaAnalysis(policy.get("psfEllipMax"),
                                                          policy.get("psfFwhmMax")))
    if data.cameraInfo.name in policy.getStringArray("doCompleteQa"):
        singleEpochAnalysisList.append(qaAnalysis.CompletenessQa(policy.get("completeMinMag"),
                                                      policy.get("completeMaxMag")))

    if data.cameraInfo.name in policy.getStringArray("doFwhm"):
        singleEpochAnalysisList.append(qaAnalysis.FwhmQaAnalysis())



    #################################
    # monitor runtimes
    #################################
    useFp = open("runtimePerformance.dat", 'w')
    useFp.write("# %-10s %-32s %10s  %16s\n" %
                ("visit", "testname", "t-elapsed", "resident-memory"))



    testset = pipeQA.TestSet(group="", label="QA-failures")
        


    ##############################################
    #
    # multi-epoch monochrome tests
    #
    ##############################################
    
    for a in multiEpochAnalysisList:

        test_t0 = time.time()

        test = str(a)
        if not re.search(testRegex, test):
            continue

        print "Running " + test

        # For debugging, it's useful to exit on failure, and get
        # the full traceback
        memory = 0
        if exceptExit:
            a.test(data, dataId)
            a.plot(data, dataId)
            memory = mem()
            a.free()

        # otherwise, we want to continue gracefully
        else:
            try:
                a.test(data, dataIdVisit)
                a.plot(data, dataIdVisit)
                memory = mem()
                a.free()
            except Exception, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                s = traceback.format_exception(exc_type, exc_value, exc_traceback)
                label = "%s_analysis" % (test)
                print "Warning: Exception in QA processing of %s" % (test)
                testset.addTest(label, 1, [0, 0], "QA exception thrown", backtrace="".join(s))

        test_tf = time.time()
        useFp.write("%-12s %-32s %9.2fs %7dk %7.2fM\n" %
                    ("multiEpoch", test, test_tf-test_t0, memory, memory/1024.0))
        useFp.flush()




    ################################################
    #
    # Single epoch tests
    #
    ################################################

    visits = data.getVisits(dataId)
    for visit in visits:

        visit_t0 = time.time()
        
        for a in singleEpochAnalysisList:

            test_t0 = time.time()
            
            test = str(a)
            if not re.search(testRegex, test):
                continue
            
            print "Running " + test + "  visit:" + str(visit)
            dataIdVisit = copy.copy(dataId)
            dataIdVisit['visit'] = visit


            # For debugging, it's useful to exit on failure, and get
            # the full traceback
            memory = 0
            if exceptExit:
                a.test(data, dataIdVisit)
                a.plot(data, dataIdVisit, showUndefined=False)
                memory = mem()
                a.free()
                
            # otherwise, we want to continue gracefully
            else:
                try:
                    a.test(data, dataIdVisit)
                except Exception, e:
                    exc_type, exc_value, exc_traceback = sys.exc_info()
                    s = traceback.format_exception(exc_type, exc_value,
                                                   exc_traceback)
                    label = "visit_%s_analysis_%s" % (visit, test)
                    print "Warning: Exception in QA processing of visit:%s, analysis:%s" % (visit, test)
                    testset.addTest(label, 1, [0, 0], "QA exception thrown", backtrace="".join(s))
                else:
                    a.plot(data, dataIdVisit, showUndefined=False)
                    memory = mem()
                    a.free()
                    
            test_tf = time.time()
            useFp.write("%-12s %-32s %9.2fs %7dk %7.2fM\n" %
                        (str(visit), test, test_tf-test_t0, memory, memory/1024.0))
            useFp.flush()
            
        data.clearCache()
    useFp.close()

#############################################################
# end
#############################################################




if __name__ == '__main__':
    
    ########################################################################
    # command line arguments and options
    ########################################################################
    
    parser = optparse.OptionParser(usage=__doc__)
    parser.add_option("-v", "--visit", default="-1",
                      help="Specify visit as regex. Use neg. number for last 'n' visits. (default=%default)")
    parser.add_option("-c", "--ccd", default=".*",
                      help="Specify ccd as regex (default=%default)")
    parser.add_option("-C", "--camera", default=None,
		      help="Specify a camera and override auto-detection (default=%default)")
    parser.add_option("-e", "--exceptExit", default=False, action='store_true',
                      help="Don't capture exceptions, fail and exit (default=%default)")
    parser.add_option("-r", "--raft", default=".*",
                      help="Specify raft as regex (default=%default)")
    parser.add_option("-R", "--rerun", default=None,
                      help="Rerun to analyse - only valid for hsc/suprimecam (default=%default)")
    parser.add_option("-s", "--snap", default=".*",
                      help="Specify snap as regex (default=%default)")
    parser.add_option("-t", "--test", default=".*",
                      help="Regex specifying which QaAnalysis to run (default=%default)")
    parser.add_option("-V", "--verbosity", default=1,
                      help="Trace level for lsst.testing.pipeQA")
    
    opts, args = parser.parse_args()

    if len(args) != 1:
        parser.print_help()
        sys.exit(1)

    dataId = {
        'visit': opts.visit,
        'ccd': opts.ccd,
        'raft': opts.raft,
        'snap': opts.snap,
        }
    rerun = opts.rerun
    dataset, = args

    Trace.setVerbosity('lsst.testing.pipeQA', int(opts.verbosity))
    
    main(dataset, dataId, rerun, opts.test, opts.camera, opts.exceptExit)
