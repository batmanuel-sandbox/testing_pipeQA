#!/usr/bin/env python
# Original filename: bin/pipeQa.py
#
# Author: 
# Email: 
# Date: Mon 2011-04-11 13:11:01
# 
# Summary: 
# 

"""
%prog [options]
"""

import sys
import re
import argparse
import os
import datetime

import numpy

import lsst.testing.displayQA         as dispQA
import lsst.testing.pipeQA.figures as qaFig
import lsst.testing.pipeQA as pqa

import hsc.pipe.base.camera as hscCamera

class QuickInfo(object):
    def __init__(self, filename, displayName):
        self.filename = filename
        self.displayName = displayName
        

#############################################################
#
# Main body of code
#
#############################################################

def main(rerun, visits, ccds, camera="suprimecam", testRegex=".*"):

    
    root = os.path.join(os.getenv('SUPRIME_DATA_DIR'), "SUPA")
    calib = os.path.join(os.getenv('SUPRIME_DATA_DIR'), "SUPA", "CALIB")
    butler = hscCamera.getButler('suprimecam', rerun=rerun, root=root)

    if camera == 'suprimecam':
        camInfo = pqa.SuprimecamCameraInfo(mit=False)
    elif camera == 'hsc':
        camInfo = pqa.HscCameraInfo()
    else:
        raise ValueError, "Unknown camera."

    if False:
        detList = []
        for ccdName,ccd in camInfo.sensors.items():
            ix, iy = ccd.getCenterPixel()
            detList.append([ccdName, ix, iy])
        prev = None
        for arr in sorted(detList, key=lambda d: (d[2], d[1]))[::-1]:
            if prev and prev != arr[2]:
                print ""
            print arr[0], " ",
            prev = arr[2]
    
    figures = [
        QuickInfo("ossThumb",            "oss.Thumb"),
        QuickInfo("flattenedThumb",      "flattened.Thumb"),
        QuickInfo("plotEllipseGrid",     "ellipse.Grid"),
        QuickInfo("plotEllipticityMap",  "elly.Map"),
        QuickInfo("plotSeeingMap",       "seeing.Map"),
        QuickInfo("plotEllipseMap",      "ellipse.Map"),
        QuickInfo("plotFwhmGrid",        "fwhm.Grid"),
        QuickInfo("plotSeeingRobust",    "seeing.Robust"),
        QuickInfo("plotEllipticityGrid", "elly.Grid"),
        QuickInfo("plotMagHist",         "magHist"),
        QuickInfo("plotSeeingRough",     "seeing.Rough"),
        ]
    
    
    for visit in visits:
        print "Running " + str(visit)
        
        for info in figures:

            f, flabel = info.filename, info.displayName

            if not re.search(testRegex, f):
                continue
            
            ts = dispQA.TestSet(group=str(visit), label=flabel)
            print "   ..."+f

            nobjs = {}
            for ccd in ccds:
                dataId = {'visit': visit, 'ccd': ccd}
                raftName, ccdName = camInfo.getRaftAndSensorNames(dataId)
                areaLabel = camInfo.getDetectorName(raftName, ccdName)

                print "   CCD "+str(ccd)+ " " + areaLabel

                meta = butler.get('calexp_md', dataId)
                nobj = meta.get('NOBJ_MATCHED')
                nobjs[areaLabel] = nobj

                ts.addTest("nObj", nobj, [0.0, 1.0e4], "Number of matched objects", areaLabel=areaLabel)

                camel = f+"_filename"
                figNames = butler.get(camel, dataId)
                caption = "Figure " + f
                if os.path.exists(figNames[0]):
                    ts.addFigureFile(figNames[0], caption, areaLabel=areaLabel)
                else:
                    print "Warning: File does not exist ... "+figNames[0]


            base = "fpa"+f
            dumData, dumMap = ts.unpickle(base, [None, None])
            fpa = qaFig.FpaQaFigure(camInfo, data=dumData, map=dumMap)

            for r, cDict in fpa.data.items():
                for c, value in cDict.items():
                    areaLabel = camInfo.getDetectorName(r, c)
                    if areaLabel in nobjs:
                        fpa.data[r][c] = nobjs[areaLabel]
                        fpa.map[r][c] = "%d" % (nobjs[areaLabel])

            fpa.makeFigure(vlimits=[0, 1.0e4], title=f, showUndefined=True,
                           failLimits=[0.0, 1.0e4], cmap="gist_heat_r")
            ts.addFigure(fpa, "fpa"+f+".png", "Figure of "+f, navMap=True)

            
def parseRange(s):
    values = []
    for ss in s.split(":"):
        ss_list = map(int, ss.split("-"))
        if len(ss_list) == 1:
            values += ss_list
        elif len(ss_list) == 2:
            values += range(ss_list[0], ss_list[1]+1)
    return values

        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("rerun", help="Rerun for the data to be run.")
    parser.add_argument("visits", help="Visits to run.  Use colon to separate values.  Use dash to denote range.")
    parser.add_argument("-C",  "--camera", default="suprimecam",
                        help="Specify camera (default=%default)")
    parser.add_argument("-c",  "--ccds", default="0-9",
                        help="Ccds to run.  Use colon to separate values.  Use dash to denote range.")
    parser.add_argument("-t", "--testRegex", default=".*",
                        help="regular expression to match tests to be run (default=%default)")
    args = parser.parse_args()

    visits = parseRange(args.visits)
    ccds   = parseRange(args.ccds)
    
    main(args.rerun, visits, ccds, testRegex=args.testRegex, camera=args.camera)
    
