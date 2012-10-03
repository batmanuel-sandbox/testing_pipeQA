from QaDataUtils import QaDataUtils


class HscQaDataUtils(QaDataUtils):

    def __init__(self):
        QaDataUtils.__init__(self)

        self.names.insert(0, "RefId")
        self.types["RefId"] = "L"
        
        
    def getSourceSetNameList(self):
        """Associate Source accessor names to database columns in a list of pairs. """

        accessors = [
            #["Id",                           "sourceId" ], #"objectId"                      ],
            ['RefId',                        'ref_id',                         ],
            ["Ra",                           "ra2000",                         ],
            ["Dec",                          "dec2000",                        ],
            #["RaErrForWcs",                  "raSigmaForWcs",                 ],
            #["DecErrForWcs",                 "declSigmaForWcs",               ],
            #["RaErrForDetection",            "raSigmaForDetection",           ],
            #["DecErrForDetection",           "declSigmaForDetection",         ],
            #["XFlux",                        "xFlux",                         ],
            #["XFluxErr",                     "xFluxSigma",                    ],
            #["YFlux",                        "yFlux",                         ],
            #["YFluxErr",                     "yFluxSigma",                    ],
            #["RaFlux",                       "raFlux",                        ],
            #["RaFluxErr",                    "raFluxSigma",                   ],
            #["DecFlux",                      "declFlux",                      ],
            #["DecFluxErr",                   "declFluxSigma",                 ],
            #["XPeak",                        "xPeak",                         ],
            #["YPeak",                        "yPeak",                         ],
            #["RaPeak",                       "raPeak",                        ],
            #["DecPeak",                      "declPeak",                      ],
            ["XAstrom",                      "centroid_sdss_x",                ],
            #["XAstromErr",                   "xAstromSigma",                  ],
            ["YAstrom",                      "centroid_sdss_y",                ],
            #["YAstromErr",                   "yAstromSigma",                  ],
            #["RaAstrom",                     "raAstrom",                      ],
            #["RaAstromErr",                  "raAstromSigma",                 ],
            #["DecAstrom",                    "declAstrom",                    ],
            #["DecAstromErr",                 "declAstromSigma",               ],
            #["TaiMidPoint",                  "taiMidPoint",                   ],
            #["TaiRange",                     "taiRange",                      ],
            ["PsfFlux",                      "flux_psf",                       ],
            ["PsfFluxErr",                   "flux_psf_e",                     ],
            ["ApFlux",                       "flux_sinc",                      ],
            ["ApFluxErr",                    "flux_sinc_e",                    ],
            ["ModelFlux",                    "flux_gaussian",                  ],
            ["ModelFluxErr",                 "flux_gaussian_e",                ],
            #["ModelFlux",                    "flux_ESG",                      ], 
            #["ModelFluxErr",                 "flux_ESG_Sigma",                ],
            ["InstFlux",                     "flux_gaussian",                  ],
            ["InstFluxErr",                     "flux_gaussian_e",             ],
            #["InstFlux",                      "flux_Gaussian",                ], 
            #["InstFluxErr",                  "flux_Gaussian_Sigma",           ],
            #["NonGrayCorrFlux",              "nonGrayCorrFlux",               ],
            #["NonGrayCorrFluxErr",           "nonGrayCorrFluxSigma",          ],
            #["AtmCorrFlux",                  "atmCorrFlux",                   ],
            #["AtmCorrFluxErr",               "atmCorrFluxSigma",              ],
            #["ApDia",                        "apDia",                         ],
            ["Ixx",                          "shape_sdss_xx",                  ],
            #["IxxErr",                       "ixxSigma",                      ],
            ["Iyy",                          "shape_sdss_yy",                  ],
            #["IyyErr",                       "iyySigma",                      ],
            ["Ixy",                          "shape_sdss_xy",                  ],
            #["IxyErr",                       "ixySigma",                      ],
            #["PsfIxx",                       "psfIxx",                        ],
            #["PsfIxxErr",                    "psfIxxSigma",                   ],
            #["PsfIyy",                       "psfIyy",                        ],
            #["PsfIyyErr",                    "psfIyySigma",                   ],
            #["PsfIxy",                       "psfIxy",                        ],
            #["PsfIxyErr",                    "psfIxySigma",                   ],
            #["Resolution",                   "resolution_SG",                 ],
            #["E1",                           "e1_SG",                         ],
            #["E1Err",                        "e1_SG_Sigma",                   ],
            #["E2",                           "e2_SG",                         ],
            #["E2Err",                        "e2_SG_Sigma",                   ],
            #["Shear1",                       "shear1_SG",                     ],
            #["Shear1Err",                    "shear1_SG_Sigma",               ],
            #["Shear2",                       "shear2_SG",                     ],
            #["Shear2Err",                    "shear2_SG_Sigma",               ],
            #["Sigma",                        "sourceWidth_SG",                ],
            #["SigmaErr",                     "sourceWidth_SG_Sigma",          ],
            #["ShapeStatus",                  "shapeStatus",                   ],
            #["Snr",                          "snr",                           ],
            #["Chi2",                         "chi2",                          ],
            #["FlagForAssociation",           "flagForAssociation",            ],
            #["FlagForDetection",             "flagForDetection",              ],
            #["FlagForWcs",                   "flagForWcs",                    ],

            # source
            ["FlagBadCentroid",               "flag_badctd",                   ],
            ["FlagPixSaturCen",               "flag_pixsttctr",                ],
            ["FlagPixInterpCen",              "flag_pixiplctr",                ],
            ["FlagPixEdge",                   "flag_pixedg",                   ],
            ["FlagNegative",                  "flag_neg",                      ],

            #["FlagBadCentroid",               "flag005",                       ],
            #["FlagPixSaturCen",               "flag011",                       ],
            #["FlagPixInterpCen",              "flag009",                       ],
            #["FlagPixEdge",                   "flag007",                       ],
            #["FlagNegative",                  "flag004",                       ],
            
            # icsource
            #["FlagBadCentroid",               "flag028", ],
            #["FlagPixSaturCen",               "flag034", ],
            #["FlagPixInterpCen",              "flag032", ],
            #["FlagPixEdge",                   "flag030", ],
            #["FlagNegative",                  "flag001", ],

            # depricated
            #["FlagPixSaturCen",               "flag%03d" % (dummyMask.getMaskPlane("SAT")+offset), ],
            #["FlagPixInterpCen",              "flag%03d" % (dummyMask.getMaskPlane("INTRP")+offset), ],
            #["FlagPixEdge",                   "flag%03d" % (dummyMask.getMaskPlane("EDGE")+offset), ],
            #["FlagNegative",                  "flag%03d" % (dummyMask.getMaskPlane("DETECTED_NEGATIVE")+offset), ],
            ["Extendedness",                  "classification_extendedness",     ],
            ]
        return accessors



    def getSceNameList(self, dataIdNames, replacements={}):
        """Associate SourceCcdExposure names to database columns in a list of pairs. """

        nameList = [ ['scienceCcdExposureId', 'frame_id' ] ] + dataIdNames
        nameList += [
            #['visit',                'visit'                ],
            #['raft',                 'raft'                 ],
            #['raftName',             'raftName'             ],
            #['ccd',                  'ccdname'                  ],
            #['ccdName',              'ccdName'              ],
            #['filterId',             'filterId'             ],
            ['filterName',           'filter'           ],
            ['ra',                   'ra'                   ],
            ['decl',                 'decl'                 ],
            #['equinox',              'equinox'              ],
            #['raDeSys',              'raDeSys'              ],
            #['ctype1',               'ctype1'               ],
            #['ctype2',               'ctype2'               ],
            #['crpix1',               'crpix1'               ],
            #['crpix2',               'crpix2'               ],
            #['crval1',               'crval1'               ],
            #['crval2',               'crval2'               ],
            #['cd1_1',                'cd1_1'                ],
            #['cd1_2',                'cd1_2'                ],
            #['cd2_1',                'cd2_1'                ],
            #['cd2_2',                'cd2_2'                ],
            #['llcRa',                'llcRa'                ],
            #['llcDecl',              'llcDecl'              ],
            #['ulcRa',                'ulcRa'                ],
            #['ulcDecl',              'ulcDecl'              ],
            #['urcRa',                'urcRa'                ],
            #['urcDecl',              'urcDecl'              ],
            #['lrcRa',                'lrcRa'                ],
            #['lrcDecl',              'lrcDecl'              ],
            #['taiMjd',               'taiMjd'               ],
            #['obsStart',             'obsStart'             ],
            #['expMidpt',             'expMidpt'             ],
            ['expTime',              'exptime'              ],
            #['nCombine',             'nCombine'             ],
            #['binX',                 'binX'                 ],
            #['binY',                 'binY'                 ],
            #['readNoise',            'readNoise'            ],
            #['saturationLimit',      'saturationLimit'      ],
            #['gainEff',              'gainEff'              ],
            ['zeropt',               'zeropt'               ],
            ['fluxMag0',             'magzero'             ],
            ['fluxMag0Sigma',        'magzero_rms'        ],
            ['fwhm',                 'seeing'                 ],
            ]


        for arr in nameList:
            a, b = arr
            if a in replacements:
                arr[1] = replacements[a]
        
        return nameList

