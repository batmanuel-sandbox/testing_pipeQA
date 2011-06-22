import sys, os, re, copy, time
import numpy

import lsst.pex.policy          as pexPolicy
import lsst.ap.cluster          as apCluster

#######################################################################
#
#
#
#######################################################################
class QaData(object):
    """Base class for QA data retrieval."""

    #######################################################################
    #
    #######################################################################
    def __init__(self, label, rerun, cameraInfo):
        """
        @param label The name of this data set
        @param rerun The rerun to retrieve
        @param cameraInfo A cameraInfo object containing specs on the camera
        """
        
        self.label = label
        self.rerun = rerun
        self.cameraInfo = cameraInfo
        self.dataInfo = self.cameraInfo.dataInfo
        
        self.dataIdNames   = []
        self.dataIdDiscrim = []
        for array in self.dataInfo:
            dataIdName, dataIdDiscrim = array
            self.dataIdNames.append(dataIdName)
            self.dataIdDiscrim.append(dataIdDiscrim)


        self.initCache()

        self.loadDepth = 0
        self.lastPrint = None
        self.t0 = []

    def printStartLoad(self, message):
        if self.loadDepth > 0:
            print "\n", " "*4*self.loadDepth, message,
        else:
            print message,
        sys.stdout.flush()
        self.loadDepth += 1
        self.lastPrint = 0
        t0 = time.time()
        self.t0.append(t0)
        

    def printMidLoad(self, message):
        print message,
        sys.stdout.flush()

    def printStopLoad(self):
        t0 = self.t0[-1]
        self.t0 = self.t0[:-1]
        t_final = time.time()
        t_elapsed = t_final - t0
        done =  "done (%.2fs)." % t_elapsed
        if self.loadDepth > 1:
            if self.lastPrint == 1:
                print "\n", " "*4*(self.loadDepth-1), done
            else:
                print done,
        else:
            if self.lastPrint == 1:
                print "\n"+done
            else:
                print done
        sys.stdout.flush()
        self.loadDepth -= 1
        self.lastPrint = 1
        

    def initCache(self):
        """Initialize all internal cache attributes. """

        # cache the dataId requests
        # they may contain regexes ... we won't know if our cached sourceSets have
        #   all the entries that match unless we redo the query
        #   But, if we've already done the identical query, we know we have everything
        self.queryCache = {}
        self.columnQueryCache = {}

        # cache source sets to avoid reloading the same thing
        self.sourceSetCache = {}
        self.sourceSetColumnCache = {}

        self.matchQueryCache = {}
        self.matchListCache = {}

        self.refObjectQueryCache = {}
        self.refObjectCache = {}
        
        # cache calexp info, but not the MaskedImage ... it's too big.
        self.calexpQueryCache = {}
        self.calexpCache = {}
        self.wcsCache = {}
        self.detectorCache = {}
        self.raftDetectorCache = {}
        self.filterCache = {}
        self.calibCache = {}

        # store the explicit dataId (ie. no regexes) for each key used in a cache
        self.dataIdLookup = {}

        self.cacheList = {
            "query"         : self.queryCache,  
            "columnQuery"   : self.columnQueryCache,
            "sourceSet"     : self.sourceSetCache,
            "sourceSetColumn"  : self.sourceSetColumnCache,
            "matchQuery"    : self.matchQueryCache,
            "matchList"     : self.matchListCache,
            "refObjectQuery": self.refObjectQueryCache,
            "refObject"     : self.refObjectCache,
            "calexpQuery"   : self.calexpQueryCache,
            "calexp"        : self.calexpCache, 
            "wcs"           : self.wcsCache,    
            "detector"      : self.detectorCache,
            "raftDetector"  : self.raftDetectorCache,
            "filter"        : self.filterCache, 
            "calib"         : self.calibCache,  
            "dataIdLookup"  : self.dataIdLookup,
            }


    def clearCache(self):
        """Reset all internal cache attributes."""
        for cache in self.cacheList.values():
            for key in cache.keys():
                del cache[key]
        self.initCache()

    def printCache(self):
        for name, cache in self.cacheList.items():
            n = 0
            for key in cache:
                if hasattr(cache[key], "__len__"):
                    n += len(cache[key])
            print name, n
                

    def getDataName(self):
        """Get a string representation of ourself."""
        # should this be __str__ or __repr__ ?
        return self.label+" rerun="+str(self.rerun)
        


    def getSourceSetColumnsBySensor(self, dataIdRegex, accessors):
        """Get a specified Source field from all sources in SourceSet as a numpy array.
        
        @param dataIdRegex dataId dict with regular expressions for data to retrieve
        @param accessors  List of accessor method names (as string without 'get' prepended)
        """

        dataIdStr = self._dataIdToString(dataIdRegex)

        # if they want a specific dataId and we have it ....
        ssTDict = {}
        if self.sourceSetColumnCache.has_key(dataIdStr):
            ssTDict[dataIdStr] = {}
            haveIt = True
            for accessor in accessors:
                if self.sourceSetColumnCache[dataIdStr].has_key(accessor):
                    ssTDict[dataIdStr][accessor] = self.sourceSetColumnCache[dataIdStr][accessor]
                else:
                    haveIt = False
                    break
            if haveIt:
                return ssTDict

        # if they've made this exact query before ... we must have it!
        if False:
            ssTDict = {}
            if self.columnQueryCache.has_key(dataIdStr+"-"+accessor):
                for k, ssDict in self.sourceSetColumnCache():
                    if re.search(dataIdStr, k):
                        if not ssTDict.has_key(k):
                            ssTDict[k] = {}
                        ssTDict[k][accessor] = ssDict[accessor]
                return ssTDict

        # get it and put the transpose in the cache
        # return a copy of what we cached.
        ssDict = self.getSourceSetBySensor(dataIdRegex)
        ssTDict = {}
        for k, ss in ssDict.items():
            if not self.sourceSetColumnCache.has_key(k):
                self.sourceSetColumnCache[k] = {}
            ssTDict[k] = {}
            for accessor in accessors:
                tmp = numpy.array([])
                for s in ss:
                    method = getattr(s, "get"+accessor)
                    value = method()
                    tmp = numpy.append(tmp, value)
                self.sourceSetColumnCache[k][accessor] = tmp
                ssTDict[k][accessor] = tmp

        #self.transposeQueryCache[dataIdStr+'-'+accessor] = True
        
        return ssTDict




    def getWcsBySensor(self, dataIdRegex):
        """Get a dict of Wcs objects with sensor ids as keys.
        
        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        """
        return self.getCalexpEntryBySensor(self.wcsCache, dataIdRegex)
    def getDetectorBySensor(self, dataIdRegex):
        """Get a dict of Detector objects with sensor ids as keys.
        
        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        """
        return self.getCalexpEntryBySensor(self.detectorCache, dataIdRegex)
    def getFilterBySensor(self, dataIdRegex):
        """Get a dict of Filter objects with sensor ids as keys.
        
        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        """
        return self.getCalexpEntryBySensor(self.filterCache, dataIdRegex)
    def getCalibBySensor(self, dataIdRegex):
        """Get a dict of Calib objects with sensor ids as keys.
        
        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        """
        return self.getCalexpEntryBySensor(self.calibCache, dataIdRegex)
    def getCalexpBySensor(self, dataIdRegex):
        """Get a dict of Calib objects with sensor ids as keys.
        
        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        """
        return self.getCalexpEntryBySensor(self.calexpCache, dataIdRegex)
    

    def verifyDataIdKeys(self, dataIdKeys, raiseOnFailure=True):
        """Verify that what we're asked for makes sense for this camera (ie. ccd vs. sensor).

        @param dataIdRegex dataId dictionary with regular expressions to specify data to retrieve
        @param raiseOnFailure Raise an exception if verification fails.
        """
        missingKeys = []
        for key in dataIdKeys:
            if not key in self.dataIdNames:
                missingKeys.append(key)
        if len(missingKeys) > 0:
            keyStr = ",".join(missingKeys)
            if raiseOnFailure:
                raise Exception("Key(s): "+keyStr+" not valid for camera "+str(self.cameraInfo))
            return False
        return True



    def getSourceClusters(self, dataIdRegex, minClusterSize=2):
        """Get apClusters for all Sources matching dataIdRegex."""

        #@param epsilonArcsec Matching distance
        epsilonArcsec = 0.5
        #@param minNeighbors Fewest neighbors to accept
        minNeighbors = 2
        #@param pointsPerLeaf who knows?
        pointsPerLeaf = 100
        #@param leafExtentThresholdArcsec Drawing a blank here too.
        leafExtentThresholdArcsec = 0.5

        policy = pexPolicy.Policy()
        policy.set("epsilonArcsec", epsilonArcsec)
        policy.set("minNeighbors", minNeighbors)
        policy.set("pointsPerLeaf", pointsPerLeaf)
        policy.set("leafExtentThresholdArcsec", leafExtentThresholdArcsec)

        sources = self.getSourceSet(dataIdRegex)
        sourceClustersAll = apCluster.cluster(sources, policy)

        sourceClusters = []
        for sc in sourceClustersAll:
            if len(sc) >= minClusterSize:
                sourceClusters.append(sc)
                
        return sourceClusters


    #######################################################################
    #
    #######################################################################
    def _dataTupleToString(self, dataTuple):
        """Represent a dataTuple as a string.

        @param dataTuple The dataTupe to be converted.
        """
        
        s = []
        for i in xrange(len(self.dataIdNames)):
            name = self.dataIdNames[i]
            value = re.sub("[,]", "", str(dataTuple[i]))
            s.append(name + value)
        return "-".join(s)

    #######################################################################
    # utility to convert a data tuple to a dictionary using dataId keys
    #######################################################################
    def _dataTupleToDataId(self, dataTuple):
        """Convert a dataTuple to a dataId dict.

        @param dataTuple The dataTuple to be converted.
        """
        
        dataId = {}
        for i in xrange(len(self.dataIdNames)):
            dataIdName = self.dataIdNames[i]
            dataId[dataIdName] = dataTuple[i]
        return dataId

    #######################################################################
    # utility to convert a dataId dictionary to a tuple
    #######################################################################
    def _dataIdToDataTuple(self, dataId):
        """Convert a dataId to a dataTuple

        @param dataId The dataId to be converted.
        """
        
        # if snap isn't specified, we'll add it.
        dataIdCopy = copy.copy(dataId)
        if not dataIdCopy.has_key('snap'):
            dataIdCopy['snap'] = '0'
            
        dataList = []
        for i in xrange(len(self.dataIdNames)):
            dataIdName = self.dataIdNames[i]
            if dataIdCopy.has_key(dataIdName):
                dataList.append(dataIdCopy[dataIdName])
            else:
                raise Exception("key: "+dataIdName+" not in dataId: "+ str(dataIdCopy))
        return tuple(dataList)

    def _dataIdToString(self, dataId):
        """Convert a dataId dict to a string.

        @param dataId The dataId to be converted
        """
        return self._dataTupleToString(self._dataIdToDataTuple(dataId))
    

    def keyStringsToVisits(self, keyList):
        """Extract a list of visits from a list of sensor keys.

        @param keyList List of keys to have visits extracted from.
        """
        
        visits = {}
        for key in keyList:
            visit = str(self.dataIdLookup[key]['visit'])
            visits[visit] = True
        return visits.keys()

    
    #########################################################
    # pure virtual methods
        
    def getSourceSet(self, dataIdRegex):
        """Get a SourceSet of all Sources matching dataId.

        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    def getSourceSetBySensor(self, dataIdRegex):
        """Get a dict of all Sources matching dataId, with sensor name as dict keys.

        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    def getMatchListBySensor(self, dataIdRegex):
        """Get a dict of all SourceMatches matching dataId, with sensor name as dict keys.

        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    def getCalexpEntryBySensor(self, cache, dataIdRegex):
        """Fill and return the dict for a specified calexp cache.

        @param cache The cache dictionary to return
        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    def getVisits(self, dataIdRegex):
        """Get a list of all visits matching dataIdRegex

        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    def loadCalexp(self, dataIdRegex):
        """Load the calexp data for data matching dataIdRegex.

        @param dataIdRegex dataId dict of regular expressions for data to be retrieved
        """
        pass
    
