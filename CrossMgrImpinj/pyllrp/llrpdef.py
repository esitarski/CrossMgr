#-----------------------------------------------------------
# DO NOT EDIT!
# MACHINE GENERATED from llrp-1x0-def.xml
#
# Created: 2013-04-10 16:42:06.328000 
#-----------------------------------------------------------
enums = [
 {
  "choices": [
   [
    0, 
    "Unspecified"
   ], 
   [
    1, 
    "EPCGlobalClass1Gen2"
   ]
  ], 
  "name": "AirProtocols"
 }, 
 {
  "choices": [
   [
    0, 
    "All"
   ], 
   [
    1, 
    "General_Device_Capabilities"
   ], 
   [
    2, 
    "LLRP_Capabilities"
   ], 
   [
    3, 
    "Regulatory_Capabilities"
   ], 
   [
    4, 
    "LLRP_Air_Protocol_Capabilities"
   ]
  ], 
  "name": "GetReaderCapabilitiesRequestedData"
 }, 
 {
  "choices": [
   [
    0, 
    "Unspecified"
   ], 
   [
    1, 
    "US_FCC_Part_15"
   ], 
   [
    2, 
    "ETSI_302_208"
   ], 
   [
    3, 
    "ETSI_300_220"
   ], 
   [
    4, 
    "Australia_LIPD_1W"
   ], 
   [
    5, 
    "Australia_LIPD_4W"
   ], 
   [
    6, 
    "Japan_ARIB_STD_T89"
   ], 
   [
    7, 
    "Hong_Kong_OFTA_1049"
   ], 
   [
    8, 
    "Taiwan_DGT_LP0002"
   ], 
   [
    9, 
    "Korea_MIC_Article_5_2"
   ]
  ], 
  "name": "CommunicationsStandard"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Inactive"
   ], 
   [
    2, 
    "Active"
   ]
  ], 
  "name": "ROSpecState"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Immediate"
   ], 
   [
    2, 
    "Periodic"
   ], 
   [
    3, 
    "GPI"
   ]
  ], 
  "name": "ROSpecStartTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Duration"
   ], 
   [
    2, 
    "GPI_With_Timeout"
   ]
  ], 
  "name": "ROSpecStopTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Duration"
   ], 
   [
    2, 
    "GPI_With_Timeout"
   ], 
   [
    3, 
    "Tag_Observation"
   ]
  ], 
  "name": "AISpecStopTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Upon_Seeing_N_Tags_Or_Timeout"
   ], 
   [
    1, 
    "Upon_Seeing_No_More_New_Tags_For_Tms_Or_Timeout"
   ], 
   [
    2, 
    "N_Attempts_To_See_All_Tags_In_FOV_Or_Timeout"
   ]
  ], 
  "name": "TagObservationTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Duration"
   ], 
   [
    2, 
    "N_Iterations_Through_Frequency_Range"
   ]
  ], 
  "name": "RFSurveySpecStopTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Active"
   ]
  ], 
  "name": "AccessSpecState"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Operation_Count"
   ]
  ], 
  "name": "AccessSpecStopTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "All"
   ], 
   [
    1, 
    "Identification"
   ], 
   [
    2, 
    "AntennaProperties"
   ], 
   [
    3, 
    "AntennaConfiguration"
   ], 
   [
    4, 
    "ROReportSpec"
   ], 
   [
    5, 
    "ReaderEventNotificationSpec"
   ], 
   [
    6, 
    "AccessReportSpec"
   ], 
   [
    7, 
    "LLRPConfigurationStateValue"
   ], 
   [
    8, 
    "KeepaliveSpec"
   ], 
   [
    9, 
    "GPIPortCurrentState"
   ], 
   [
    10, 
    "GPOWriteData"
   ], 
   [
    11, 
    "EventsAndReports"
   ]
  ], 
  "name": "GetReaderConfigRequestedData"
 }, 
 {
  "choices": [
   [
    0, 
    "MAC_Address"
   ], 
   [
    1, 
    "EPC"
   ]
  ], 
  "name": "IdentificationType"
 }, 
 {
  "choices": [
   [
    0, 
    "Null"
   ], 
   [
    1, 
    "Periodic"
   ]
  ], 
  "name": "KeepaliveTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Low"
   ], 
   [
    1, 
    "High"
   ], 
   [
    2, 
    "Unknown"
   ]
  ], 
  "name": "GPIPortState"
 }, 
 {
  "choices": [
   [
    0, 
    "None"
   ], 
   [
    1, 
    "Upon_N_Tags_Or_End_Of_AISpec"
   ], 
   [
    2, 
    "Upon_N_Tags_Or_End_Of_ROSpec"
   ]
  ], 
  "name": "ROReportTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Whenever_ROReport_Is_Generated"
   ], 
   [
    1, 
    "End_Of_AccessSpec"
   ]
  ], 
  "name": "AccessReportTriggerType"
 }, 
 {
  "choices": [
   [
    0, 
    "Upon_Hopping_To_Next_Channel"
   ], 
   [
    1, 
    "GPI_Event"
   ], 
   [
    2, 
    "ROSpec_Event"
   ], 
   [
    3, 
    "Report_Buffer_Fill_Warning"
   ], 
   [
    4, 
    "Reader_Exception_Event"
   ], 
   [
    5, 
    "RFSurvey_Event"
   ], 
   [
    6, 
    "AISpec_Event"
   ], 
   [
    7, 
    "AISpec_Event_With_Details"
   ], 
   [
    8, 
    "Antenna_Event"
   ]
  ], 
  "name": "NotificationEventType"
 }, 
 {
  "choices": [
   [
    0, 
    "Start_Of_ROSpec"
   ], 
   [
    1, 
    "End_Of_ROSpec"
   ], 
   [
    2, 
    "Preemption_Of_ROSpec"
   ]
  ], 
  "name": "ROSpecEventType"
 }, 
 {
  "choices": [
   [
    0, 
    "Start_Of_RFSurvey"
   ], 
   [
    1, 
    "End_Of_RFSurvey"
   ]
  ], 
  "name": "RFSurveyEventType"
 }, 
 {
  "choices": [
   [
    0, 
    "End_Of_AISpec"
   ]
  ], 
  "name": "AISpecEventType"
 }, 
 {
  "choices": [
   [
    0, 
    "Antenna_Disconnected"
   ], 
   [
    1, 
    "Antenna_Connected"
   ]
  ], 
  "name": "AntennaEventType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Failed_A_Reader_Initiated_Connection_Already_Exists"
   ], 
   [
    2, 
    "Failed_A_Client_Initiated_Connection_Already_Exists"
   ], 
   [
    3, 
    "Failed_Reason_Other_Than_A_Connection_Already_Exists"
   ], 
   [
    4, 
    "Another_Connection_Attempted"
   ]
  ], 
  "name": "ConnectionAttemptStatusType"
 }, 
 {
  "choices": [
   [
    0, 
    "M_Success"
   ], 
   [
    100, 
    "M_ParameterError"
   ], 
   [
    101, 
    "M_FieldError"
   ], 
   [
    102, 
    "M_UnexpectedParameter"
   ], 
   [
    103, 
    "M_MissingParameter"
   ], 
   [
    104, 
    "M_DuplicateParameter"
   ], 
   [
    105, 
    "M_OverflowParameter"
   ], 
   [
    106, 
    "M_OverflowField"
   ], 
   [
    107, 
    "M_UnknownParameter"
   ], 
   [
    108, 
    "M_UnknownField"
   ], 
   [
    109, 
    "M_UnsupportedMessage"
   ], 
   [
    110, 
    "M_UnsupportedVersion"
   ], 
   [
    111, 
    "M_UnsupportedParameter"
   ], 
   [
    200, 
    "P_ParameterError"
   ], 
   [
    201, 
    "P_FieldError"
   ], 
   [
    202, 
    "P_UnexpectedParameter"
   ], 
   [
    203, 
    "P_MissingParameter"
   ], 
   [
    204, 
    "P_DuplicateParameter"
   ], 
   [
    205, 
    "P_OverflowParameter"
   ], 
   [
    206, 
    "P_OverflowField"
   ], 
   [
    207, 
    "P_UnknownParameter"
   ], 
   [
    208, 
    "P_UnknownField"
   ], 
   [
    209, 
    "P_UnsupportedParameter"
   ], 
   [
    300, 
    "A_Invalid"
   ], 
   [
    301, 
    "A_OutOfRange"
   ], 
   [
    401, 
    "R_DeviceError"
   ]
  ], 
  "name": "StatusCode"
 }, 
 {
  "choices": [
   [
    0, 
    "DRV_8"
   ], 
   [
    1, 
    "DRV_64_3"
   ]
  ], 
  "name": "C1G2DRValue"
 }, 
 {
  "choices": [
   [
    0, 
    "MV_FM0"
   ], 
   [
    1, 
    "MV_2"
   ], 
   [
    2, 
    "MV_4"
   ], 
   [
    3, 
    "MV_8"
   ]
  ], 
  "name": "C1G2MValue"
 }, 
 {
  "choices": [
   [
    0, 
    "PR_ASK"
   ], 
   [
    1, 
    "SSB_ASK"
   ], 
   [
    2, 
    "DSB_ASK"
   ]
  ], 
  "name": "C1G2ForwardLinkModulation"
 }, 
 {
  "choices": [
   [
    0, 
    "Unknown"
   ], 
   [
    1, 
    "SI"
   ], 
   [
    2, 
    "MI"
   ], 
   [
    3, 
    "DI"
   ]
  ], 
  "name": "C1G2SpectralMaskIndicator"
 }, 
 {
  "choices": [
   [
    0, 
    "Unspecified"
   ], 
   [
    1, 
    "Do_Not_Truncate"
   ], 
   [
    2, 
    "Truncate"
   ]
  ], 
  "name": "C1G2TruncateAction"
 }, 
 {
  "choices": [
   [
    0, 
    "SL"
   ], 
   [
    1, 
    "Inventoried_State_For_Session_S0"
   ], 
   [
    2, 
    "Inventoried_State_For_Session_S1"
   ], 
   [
    3, 
    "Inventoried_State_For_Session_S2"
   ], 
   [
    4, 
    "Inventoried_State_For_Session_S3"
   ]
  ], 
  "name": "C1G2StateAwareTarget"
 }, 
 {
  "choices": [
   [
    0, 
    "AssertSLOrA_DeassertSLOrB"
   ], 
   [
    1, 
    "AssertSLOrA_Noop"
   ], 
   [
    2, 
    "Noop_DeassertSLOrB"
   ], 
   [
    3, 
    "NegateSLOrABBA_Noop"
   ], 
   [
    4, 
    "DeassertSLOrB_AssertSLOrA"
   ], 
   [
    5, 
    "DeassertSLOrB_Noop"
   ], 
   [
    6, 
    "Noop_AssertSLOrA"
   ], 
   [
    7, 
    "Noop_NegateSLOrABBA"
   ]
  ], 
  "name": "C1G2StateAwareAction"
 }, 
 {
  "choices": [
   [
    0, 
    "Select_Unselect"
   ], 
   [
    1, 
    "Select_DoNothing"
   ], 
   [
    2, 
    "DoNothing_Unselect"
   ], 
   [
    3, 
    "Unselect_DoNothing"
   ], 
   [
    4, 
    "Unselect_Select"
   ], 
   [
    5, 
    "DoNothing_Select"
   ]
  ], 
  "name": "C1G2StateUnawareAction"
 }, 
 {
  "choices": [
   [
    0, 
    "State_A"
   ], 
   [
    1, 
    "State_B"
   ]
  ], 
  "name": "C1G2TagInventoryStateAwareI"
 }, 
 {
  "choices": [
   [
    0, 
    "SL"
   ], 
   [
    1, 
    "Not_SL"
   ]
  ], 
  "name": "C1G2TagInventoryStateAwareS"
 }, 
 {
  "choices": [
   [
    0, 
    "Read_Write"
   ], 
   [
    1, 
    "Perma_Lock"
   ], 
   [
    2, 
    "Perma_Unlock"
   ], 
   [
    3, 
    "Unlock"
   ]
  ], 
  "name": "C1G2LockPrivilege"
 }, 
 {
  "choices": [
   [
    0, 
    "Kill_Password"
   ], 
   [
    1, 
    "Access_Password"
   ], 
   [
    2, 
    "EPC_Memory"
   ], 
   [
    3, 
    "TID_Memory"
   ], 
   [
    4, 
    "User_Memory"
   ]
  ], 
  "name": "C1G2LockDataField"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Nonspecific_Tag_Error"
   ], 
   [
    2, 
    "No_Response_From_Tag"
   ], 
   [
    3, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2ReadResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Tag_Memory_Overrun_Error"
   ], 
   [
    2, 
    "Tag_Memory_Locked_Error"
   ], 
   [
    3, 
    "Insufficient_Power"
   ], 
   [
    4, 
    "Nonspecific_Tag_Error"
   ], 
   [
    5, 
    "No_Response_From_Tag"
   ], 
   [
    6, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2WriteResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Zero_Kill_Password_Error"
   ], 
   [
    2, 
    "Insufficient_Power"
   ], 
   [
    3, 
    "Nonspecific_Tag_Error"
   ], 
   [
    4, 
    "No_Response_From_Tag"
   ], 
   [
    5, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2KillResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Insufficient_Power"
   ], 
   [
    2, 
    "Nonspecific_Tag_Error"
   ], 
   [
    3, 
    "No_Response_From_Tag"
   ], 
   [
    4, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2LockResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Tag_Memory_Overrun_Error"
   ], 
   [
    2, 
    "Tag_Memory_Locked_Error"
   ], 
   [
    3, 
    "Insufficient_Power"
   ], 
   [
    4, 
    "Nonspecific_Tag_Error"
   ], 
   [
    5, 
    "No_Response_From_Tag"
   ], 
   [
    6, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2BlockEraseResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Tag_Memory_Overrun_Error"
   ], 
   [
    2, 
    "Tag_Memory_Locked_Error"
   ], 
   [
    3, 
    "Insufficient_Power"
   ], 
   [
    4, 
    "Nonspecific_Tag_Error"
   ], 
   [
    5, 
    "No_Response_From_Tag"
   ], 
   [
    6, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "C1G2BlockWriteResultType"
 }
]
parameters = [
 {
  "fields": [
   {
    "format": "Datetime", 
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "UTCTimestamp", 
  "typeNum": 128
 }, 
 {
  "fields": [
   {
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "Uptime", 
  "typeNum": 129
 }, 
 {
  "fields": [
   {
    "name": "VendorIdentifier", 
    "type": "uintbe:32"
   }, 
   {
    "name": "ParameterSubtype", 
    "type": "uintbe:32"
   }, 
   {
    "format": "Hex", 
    "name": "Data", 
    "type": "bytesToEnd"
   }
  ], 
  "name": "Custom", 
  "typeNum": 1023
 }, 
 {
  "fields": [
   {
    "name": "MaxNumberOfAntennaSupported", 
    "type": "uintbe:16"
   }, 
   {
    "name": "CanSetAntennaProperties", 
    "type": "bool"
   }, 
   {
    "name": "HasUTCClockCapability", 
    "type": "bool"
   }, 
   {
    "name": "skip:14", 
    "type": "skip:14"
   }, 
   {
    "name": "DeviceManufacturerName", 
    "type": "uintbe:32"
   }, 
   {
    "name": "ModelName", 
    "type": "uintbe:32"
   }, 
   {
    "format": "UTF8", 
    "name": "ReaderFirmwareVersion", 
    "type": "string"
   }
  ], 
  "name": "GeneralDeviceCapabilities", 
  "parameters": [
   {
    "parameter": "ReceiveSensitivityTableEntry", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "PerAntennaReceiveSensitivityRange", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "GPIOCapabilities", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "PerAntennaAirProtocol", 
    "repeat": [
     1, 
     99999
    ]
   }
  ], 
  "typeNum": 137
 }, 
 {
  "fields": [
   {
    "name": "Index", 
    "type": "uintbe:16"
   }, 
   {
    "name": "ReceiveSensitivityValue", 
    "type": "intbe:16"
   }
  ], 
  "name": "ReceiveSensitivityTableEntry", 
  "typeNum": 139
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "ReceiveSensitivityIndexMin", 
    "type": "uintbe:16"
   }, 
   {
    "name": "ReceiveSensitivityIndexMax", 
    "type": "uintbe:16"
   }
  ], 
  "name": "PerAntennaReceiveSensitivityRange", 
  "typeNum": 149
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "AirProtocols", 
    "name": "ProtocolID", 
    "type": "array:8"
   }
  ], 
  "name": "PerAntennaAirProtocol", 
  "typeNum": 140
 }, 
 {
  "fields": [
   {
    "name": "NumGPIs", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NumGPOs", 
    "type": "uintbe:16"
   }
  ], 
  "name": "GPIOCapabilities", 
  "typeNum": 141
 }, 
 {
  "fields": [
   {
    "name": "CanDoRFSurvey", 
    "type": "bool"
   }, 
   {
    "name": "CanReportBufferFillWarning", 
    "type": "bool"
   }, 
   {
    "name": "SupportsClientRequestOpSpec", 
    "type": "bool"
   }, 
   {
    "name": "CanDoTagInventoryStateAwareSingulation", 
    "type": "bool"
   }, 
   {
    "name": "SupportsEventAndReportHolding", 
    "type": "bool"
   }, 
   {
    "name": "skip:3", 
    "type": "skip:3"
   }, 
   {
    "name": "MaxNumPriorityLevelsSupported", 
    "type": "uintbe:8"
   }, 
   {
    "name": "ClientRequestOpSpecTimeout", 
    "type": "uintbe:16"
   }, 
   {
    "name": "MaxNumROSpecs", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MaxNumSpecsPerROSpec", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MaxNumInventoryParameterSpecsPerAISpec", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MaxNumAccessSpecs", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MaxNumOpSpecsPerAccessSpec", 
    "type": "uintbe:32"
   }
  ], 
  "name": "LLRPCapabilities", 
  "typeNum": 142
 }, 
 {
  "fields": [
   {
    "name": "CountryCode", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "CommunicationsStandard", 
    "name": "CommunicationsStandard", 
    "type": "uintbe:16"
   }
  ], 
  "name": "RegulatoryCapabilities", 
  "parameters": [
   {
    "parameter": "UHFBandCapabilities", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 143
 }, 
 {
  "name": "UHFBandCapabilities", 
  "parameters": [
   {
    "parameter": "TransmitPowerLevelTableEntry", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "FrequencyInformation", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 144
 }, 
 {
  "fields": [
   {
    "name": "Index", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TransmitPowerValue", 
    "type": "intbe:16"
   }
  ], 
  "name": "TransmitPowerLevelTableEntry", 
  "typeNum": 145
 }, 
 {
  "fields": [
   {
    "name": "Hopping", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "FrequencyInformation", 
  "parameters": [
   {
    "parameter": "FrequencyHopTable", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "FixedFrequencyTable", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 146
 }, 
 {
  "fields": [
   {
    "name": "HopTableID", 
    "type": "uintbe:8"
   }, 
   {
    "name": "skip:8", 
    "type": "skip:8"
   }, 
   {
    "name": "Frequency", 
    "type": "array:32"
   }
  ], 
  "name": "FrequencyHopTable", 
  "typeNum": 147
 }, 
 {
  "fields": [
   {
    "name": "Frequency", 
    "type": "array:32"
   }
  ], 
  "name": "FixedFrequencyTable", 
  "typeNum": 148
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "Priority", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ROSpecState", 
    "name": "CurrentState", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ROSpec", 
  "parameters": [
   {
    "parameter": "ROBoundarySpec", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "ROReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 177
 }, 
 {
  "name": "ROBoundarySpec", 
  "parameters": [
   {
    "parameter": "ROSpecStartTrigger", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "ROSpecStopTrigger", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 178
 }, 
 {
  "fields": [
   {
    "enumeration": "ROSpecStartTriggerType", 
    "name": "ROSpecStartTriggerType", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ROSpecStartTrigger", 
  "parameters": [
   {
    "parameter": "PeriodicTriggerValue", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "GPITriggerValue", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 179
 }, 
 {
  "fields": [
   {
    "name": "Offset", 
    "type": "uintbe:32"
   }, 
   {
    "name": "Period", 
    "type": "uintbe:32"
   }
  ], 
  "name": "PeriodicTriggerValue", 
  "parameters": [
   {
    "parameter": "UTCTimestamp", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 180
 }, 
 {
  "fields": [
   {
    "name": "GPIPortNum", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPIEvent", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }, 
   {
    "name": "Timeout", 
    "type": "uintbe:32"
   }
  ], 
  "name": "GPITriggerValue", 
  "typeNum": 181
 }, 
 {
  "fields": [
   {
    "enumeration": "ROSpecStopTriggerType", 
    "name": "ROSpecStopTriggerType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "DurationTriggerValue", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ROSpecStopTrigger", 
  "parameters": [
   {
    "parameter": "GPITriggerValue", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 182
 }, 
 {
  "fields": [
   {
    "name": "AntennaIDs", 
    "type": "array:16"
   }
  ], 
  "name": "AISpec", 
  "parameters": [
   {
    "parameter": "AISpecStopTrigger", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "InventoryParameterSpec", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 183
 }, 
 {
  "fields": [
   {
    "enumeration": "AISpecStopTriggerType", 
    "name": "AISpecStopTriggerType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "DurationTrigger", 
    "type": "uintbe:32"
   }
  ], 
  "name": "AISpecStopTrigger", 
  "parameters": [
   {
    "parameter": "GPITriggerValue", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "TagObservationTrigger", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 184
 }, 
 {
  "fields": [
   {
    "enumeration": "TagObservationTriggerType", 
    "name": "TriggerType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "skip:8", 
    "type": "skip:8"
   }, 
   {
    "name": "NumberOfTags", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NumberOfAttempts", 
    "type": "uintbe:16"
   }, 
   {
    "name": "T", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Timeout", 
    "type": "uintbe:32"
   }
  ], 
  "name": "TagObservationTrigger", 
  "typeNum": 185
 }, 
 {
  "fields": [
   {
    "name": "InventoryParameterSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "AirProtocols", 
    "name": "ProtocolID", 
    "type": "uintbe:8"
   }
  ], 
  "name": "InventoryParameterSpec", 
  "parameters": [
   {
    "parameter": "AntennaConfiguration", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 186
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "StartFrequency", 
    "type": "uintbe:32"
   }, 
   {
    "name": "EndFrequency", 
    "type": "uintbe:32"
   }
  ], 
  "name": "RFSurveySpec", 
  "parameters": [
   {
    "parameter": "RFSurveySpecStopTrigger", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 187
 }, 
 {
  "fields": [
   {
    "enumeration": "RFSurveySpecStopTriggerType", 
    "name": "StopTriggerType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "DurationPeriod", 
    "type": "uintbe:32"
   }, 
   {
    "name": "N", 
    "type": "uintbe:32"
   }
  ], 
  "name": "RFSurveySpecStopTrigger", 
  "typeNum": 188
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "AirProtocols", 
    "name": "ProtocolID", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "AccessSpecState", 
    "name": "CurrentState", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }, 
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "AccessSpec", 
  "parameters": [
   {
    "parameter": "AccessSpecStopTrigger", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "AccessCommand", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "AccessReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 207
 }, 
 {
  "fields": [
   {
    "enumeration": "AccessSpecStopTriggerType", 
    "name": "AccessSpecStopTrigger", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OperationCountValue", 
    "type": "uintbe:16"
   }
  ], 
  "name": "AccessSpecStopTrigger", 
  "typeNum": 208
 }, 
 {
  "name": "AccessCommand", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 209
 }, 
 {
  "fields": [
   {
    "name": "LLRPConfigurationStateValue", 
    "type": "uintbe:32"
   }
  ], 
  "name": "LLRPConfigurationStateValue", 
  "typeNum": 217
 }, 
 {
  "fields": [
   {
    "enumeration": "IdentificationType", 
    "name": "IDType", 
    "type": "uintbe:8"
   }, 
   {
    "format": "Hex", 
    "name": "ReaderID", 
    "type": "array:8"
   }
  ], 
  "name": "Identification", 
  "typeNum": 218
 }, 
 {
  "fields": [
   {
    "name": "GPOPortNumber", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPOData", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "GPOWriteData", 
  "typeNum": 219
 }, 
 {
  "fields": [
   {
    "enumeration": "KeepaliveTriggerType", 
    "name": "KeepaliveTriggerType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "PeriodicTriggerValue", 
    "type": "uintbe:32"
   }
  ], 
  "name": "KeepaliveSpec", 
  "typeNum": 220
 }, 
 {
  "fields": [
   {
    "name": "AntennaConnected", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }, 
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AntennaGain", 
    "type": "intbe:16"
   }
  ], 
  "name": "AntennaProperties", 
  "typeNum": 221
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "AntennaConfiguration", 
  "parameters": [
   {
    "parameter": "RFReceiver", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "RFTransmitter", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 222
 }, 
 {
  "fields": [
   {
    "name": "ReceiverSensitivity", 
    "type": "uintbe:16"
   }
  ], 
  "name": "RFReceiver", 
  "typeNum": 223
 }, 
 {
  "fields": [
   {
    "name": "HopTableID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "ChannelIndex", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TransmitPower", 
    "type": "uintbe:16"
   }
  ], 
  "name": "RFTransmitter", 
  "typeNum": 224
 }, 
 {
  "fields": [
   {
    "name": "GPIPortNum", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Config", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }, 
   {
    "enumeration": "GPIPortState", 
    "name": "State", 
    "type": "uintbe:8"
   }
  ], 
  "name": "GPIPortCurrentState", 
  "typeNum": 225
 }, 
 {
  "fields": [
   {
    "name": "HoldEventsAndReportsUponReconnect", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "EventsAndReports", 
  "typeNum": 226
 }, 
 {
  "fields": [
   {
    "enumeration": "ROReportTriggerType", 
    "name": "ROReportTrigger", 
    "type": "uintbe:8"
   }, 
   {
    "name": "N", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ROReportSpec", 
  "parameters": [
   {
    "parameter": "TagReportContentSelector", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 237
 }, 
 {
  "fields": [
   {
    "name": "EnableROSpecID", 
    "type": "bool"
   }, 
   {
    "name": "EnableSpecIndex", 
    "type": "bool"
   }, 
   {
    "name": "EnableInventoryParameterSpecID", 
    "type": "bool"
   }, 
   {
    "name": "EnableAntennaID", 
    "type": "bool"
   }, 
   {
    "name": "EnableChannelIndex", 
    "type": "bool"
   }, 
   {
    "name": "EnablePeakRSSI", 
    "type": "bool"
   }, 
   {
    "name": "EnableFirstSeenTimestamp", 
    "type": "bool"
   }, 
   {
    "name": "EnableLastSeenTimestamp", 
    "type": "bool"
   }, 
   {
    "name": "EnableTagSeenCount", 
    "type": "bool"
   }, 
   {
    "name": "EnableAccessSpecID", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "TagReportContentSelector", 
  "typeNum": 238
 }, 
 {
  "fields": [
   {
    "enumeration": "AccessReportTriggerType", 
    "name": "AccessReportTrigger", 
    "type": "uintbe:8"
   }
  ], 
  "name": "AccessReportSpec", 
  "typeNum": 239
 }, 
 {
  "name": "TagReportData", 
  "parameters": [
   {
    "parameter": "ROSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "SpecIndex", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "InventoryParameterSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AntennaID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "PeakRSSI", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ChannelIndex", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "FirstSeenTimestampUTC", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "FirstSeenTimestampUptime", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "LastSeenTimestampUTC", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "LastSeenTimestampUptime", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "TagSeenCount", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AccessSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 240
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "EPC", 
    "type": "bitarray"
   }
  ], 
  "name": "EPCData", 
  "typeNum": 241
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "EPC", 
    "type": "uintbe:96"
   }
  ], 
  "name": "EPC_96", 
  "typeNum": 13
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ROSpecID", 
  "typeNum": 9
 }, 
 {
  "fields": [
   {
    "name": "SpecIndex", 
    "type": "uintbe:16"
   }
  ], 
  "name": "SpecIndex", 
  "typeNum": 14
 }, 
 {
  "fields": [
   {
    "name": "InventoryParameterSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "InventoryParameterSpecID", 
  "typeNum": 10
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "AntennaID", 
  "typeNum": 1
 }, 
 {
  "fields": [
   {
    "name": "PeakRSSI", 
    "type": "intbe:8"
   }
  ], 
  "name": "PeakRSSI", 
  "typeNum": 6
 }, 
 {
  "fields": [
   {
    "name": "ChannelIndex", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ChannelIndex", 
  "typeNum": 7
 }, 
 {
  "fields": [
   {
    "format": "Datetime", 
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "FirstSeenTimestampUTC", 
  "typeNum": 2
 }, 
 {
  "fields": [
   {
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "FirstSeenTimestampUptime", 
  "typeNum": 3
 }, 
 {
  "fields": [
   {
    "format": "Datetime", 
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "LastSeenTimestampUTC", 
  "typeNum": 4
 }, 
 {
  "fields": [
   {
    "name": "Microseconds", 
    "type": "uintbe:64"
   }
  ], 
  "name": "LastSeenTimestampUptime", 
  "typeNum": 5
 }, 
 {
  "fields": [
   {
    "name": "TagCount", 
    "type": "uintbe:16"
   }
  ], 
  "name": "TagSeenCount", 
  "typeNum": 8
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "AccessSpecID", 
  "typeNum": 16
 }, 
 {
  "name": "RFSurveyReportData", 
  "parameters": [
   {
    "parameter": "ROSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "SpecIndex", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "FrequencyRSSILevelEntry", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 242
 }, 
 {
  "fields": [
   {
    "name": "Frequency", 
    "type": "uintbe:32"
   }, 
   {
    "name": "Bandwidth", 
    "type": "uintbe:32"
   }, 
   {
    "name": "AverageRSSI", 
    "type": "intbe:8"
   }, 
   {
    "name": "PeakRSSI", 
    "type": "intbe:8"
   }
  ], 
  "name": "FrequencyRSSILevelEntry", 
  "typeNum": 243
 }, 
 {
  "name": "ReaderEventNotificationSpec", 
  "parameters": [
   {
    "parameter": "EventNotificationState", 
    "repeat": [
     1, 
     99999
    ]
   }
  ], 
  "typeNum": 244
 }, 
 {
  "fields": [
   {
    "enumeration": "NotificationEventType", 
    "name": "EventType", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NotificationState", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "EventNotificationState", 
  "typeNum": 245
 }, 
 {
  "name": "ReaderEventNotificationData", 
  "parameters": [
   {
    "parameter": "HoppingEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "GPIEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ROSpecEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ReportBufferLevelWarningEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ReportBufferOverflowErrorEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ReaderExceptionEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "RFSurveyEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AISpecEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AntennaEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ConnectionAttemptEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ConnectionCloseEvent", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 246
 }, 
 {
  "fields": [
   {
    "name": "HopTableID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NextChannelIndex", 
    "type": "uintbe:16"
   }
  ], 
  "name": "HoppingEvent", 
  "typeNum": 247
 }, 
 {
  "fields": [
   {
    "name": "GPIPortNumber", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPIEvent", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "GPIEvent", 
  "typeNum": 248
 }, 
 {
  "fields": [
   {
    "enumeration": "ROSpecEventType", 
    "name": "EventType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "PreemptingROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ROSpecEvent", 
  "typeNum": 249
 }, 
 {
  "fields": [
   {
    "name": "ReportBufferPercentageFull", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ReportBufferLevelWarningEvent", 
  "typeNum": 250
 }, 
 {
  "name": "ReportBufferOverflowErrorEvent", 
  "typeNum": 251
 }, 
 {
  "fields": [
   {
    "format": "UTF8", 
    "name": "Message", 
    "type": "string"
   }
  ], 
  "name": "ReaderExceptionEvent", 
  "parameters": [
   {
    "parameter": "ROSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "SpecIndex", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "InventoryParameterSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AntennaID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AccessSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "OpSpecID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 252
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "OpSpecID", 
  "typeNum": 17
 }, 
 {
  "fields": [
   {
    "enumeration": "RFSurveyEventType", 
    "name": "EventType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "SpecIndex", 
    "type": "uintbe:16"
   }
  ], 
  "name": "RFSurveyEvent", 
  "typeNum": 253
 }, 
 {
  "fields": [
   {
    "enumeration": "AISpecEventType", 
    "name": "EventType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "SpecIndex", 
    "type": "uintbe:16"
   }
  ], 
  "name": "AISpecEvent", 
  "typeNum": 254
 }, 
 {
  "fields": [
   {
    "enumeration": "AntennaEventType", 
    "name": "EventType", 
    "type": "uintbe:8"
   }, 
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "AntennaEvent", 
  "typeNum": 255
 }, 
 {
  "fields": [
   {
    "enumeration": "ConnectionAttemptStatusType", 
    "name": "Status", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ConnectionAttemptEvent", 
  "typeNum": 256
 }, 
 {
  "name": "ConnectionCloseEvent", 
  "typeNum": 257
 }, 
 {
  "fields": [
   {
    "enumeration": "StatusCode", 
    "name": "StatusCode", 
    "type": "uintbe:16"
   }, 
   {
    "format": "UTF8", 
    "name": "ErrorDescription", 
    "type": "string"
   }
  ], 
  "name": "LLRPStatus", 
  "parameters": [
   {
    "parameter": "FieldError", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ParameterError", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 287
 }, 
 {
  "fields": [
   {
    "name": "FieldNum", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "StatusCode", 
    "name": "ErrorCode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "FieldError", 
  "typeNum": 288
 }, 
 {
  "fields": [
   {
    "name": "ParameterType", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "StatusCode", 
    "name": "ErrorCode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ParameterError", 
  "parameters": [
   {
    "parameter": "FieldError", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ParameterError", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 289
 }, 
 {
  "fields": [
   {
    "name": "CanSupportBlockErase", 
    "type": "bool"
   }, 
   {
    "name": "CanSupportBlockWrite", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "MaxNumSelectFiltersPerQuery", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2LLRPCapabilities", 
  "typeNum": 327
 }, 
 {
  "name": "C1G2UHFRFModeTable", 
  "parameters": [
   {
    "parameter": "C1G2UHFRFModeTableEntry", 
    "repeat": [
     1, 
     99999
    ]
   }
  ], 
  "typeNum": 328
 }, 
 {
  "fields": [
   {
    "name": "ModeIdentifier", 
    "type": "uintbe:32"
   }, 
   {
    "enumeration": "C1G2DRValue", 
    "name": "DRValue", 
    "type": "bool"
   }, 
   {
    "name": "EPCHAGTCConformance", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "enumeration": "C1G2MValue", 
    "name": "MValue", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "C1G2ForwardLinkModulation", 
    "name": "ForwardLinkModulation", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "C1G2SpectralMaskIndicator", 
    "name": "SpectralMaskIndicator", 
    "type": "uintbe:8"
   }, 
   {
    "name": "BDRValue", 
    "type": "uintbe:32"
   }, 
   {
    "name": "PIEValue", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MinTariValue", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MaxTariValue", 
    "type": "uintbe:32"
   }, 
   {
    "name": "StepTariValue", 
    "type": "uintbe:32"
   }
  ], 
  "name": "C1G2UHFRFModeTableEntry", 
  "typeNum": 329
 }, 
 {
  "fields": [
   {
    "name": "TagInventoryStateAware", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "C1G2InventoryCommand", 
  "parameters": [
   {
    "parameter": "C1G2Filter", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "C1G2RFControl", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "C1G2SingulationControl", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 330
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2TruncateAction", 
    "name": "T", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "C1G2Filter", 
  "parameters": [
   {
    "parameter": "C1G2TagInventoryMask", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "C1G2TagInventoryStateAwareFilterAction", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "C1G2TagInventoryStateUnawareFilterAction", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 331
 }, 
 {
  "fields": [
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "Pointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "TagMask", 
    "type": "bitarray"
   }
  ], 
  "name": "C1G2TagInventoryMask", 
  "typeNum": 332
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2StateAwareTarget", 
    "name": "Target", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "C1G2StateAwareAction", 
    "name": "Action", 
    "type": "uintbe:8"
   }
  ], 
  "name": "C1G2TagInventoryStateAwareFilterAction", 
  "typeNum": 333
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2StateUnawareAction", 
    "name": "Action", 
    "type": "uintbe:8"
   }
  ], 
  "name": "C1G2TagInventoryStateUnawareFilterAction", 
  "typeNum": 334
 }, 
 {
  "fields": [
   {
    "name": "ModeIndex", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Tari", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2RFControl", 
  "typeNum": 335
 }, 
 {
  "fields": [
   {
    "name": "Session", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "TagPopulation", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TagTransitTime", 
    "type": "uintbe:32"
   }
  ], 
  "name": "C1G2SingulationControl", 
  "parameters": [
   {
    "parameter": "C1G2TagInventoryStateAwareSingulationAction", 
    "repeat": [
     0, 
     1
    ]
   }
  ], 
  "typeNum": 336
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2TagInventoryStateAwareI", 
    "name": "I", 
    "type": "bool"
   }, 
   {
    "enumeration": "C1G2TagInventoryStateAwareS", 
    "name": "S", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "C1G2TagInventoryStateAwareSingulationAction", 
  "typeNum": 337
 }, 
 {
  "name": "C1G2TagSpec", 
  "parameters": [
   {
    "parameter": "C1G2TargetTag", 
    "repeat": [
     1, 
     99999
    ]
   }
  ], 
  "typeNum": 338
 }, 
 {
  "fields": [
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "Match", 
    "type": "bool"
   }, 
   {
    "name": "skip:5", 
    "type": "skip:5"
   }, 
   {
    "name": "Pointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "TagMask", 
    "type": "bitarray"
   }, 
   {
    "format": "Hex", 
    "name": "TagData", 
    "type": "bitarray"
   }
  ], 
  "name": "C1G2TargetTag", 
  "typeNum": 339
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "WordPointer", 
    "type": "uintbe:16"
   }, 
   {
    "name": "WordCount", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2Read", 
  "typeNum": 341
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "WordPointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "WriteData", 
    "type": "array:16"
   }
  ], 
  "name": "C1G2Write", 
  "typeNum": 342
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "KillPassword", 
    "type": "uintbe:32"
   }
  ], 
  "name": "C1G2Kill", 
  "typeNum": 343
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }
  ], 
  "name": "C1G2Lock", 
  "parameters": [
   {
    "parameter": "C1G2LockPayload", 
    "repeat": [
     1, 
     99999
    ]
   }
  ], 
  "typeNum": 344
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2LockPrivilege", 
    "name": "Privilege", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "C1G2LockDataField", 
    "name": "DataField", 
    "type": "uintbe:8"
   }
  ], 
  "name": "C1G2LockPayload", 
  "typeNum": 345
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "WordPointer", 
    "type": "uintbe:16"
   }, 
   {
    "name": "WordCount", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2BlockErase", 
  "typeNum": 346
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MB", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }, 
   {
    "name": "WordPointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "WriteData", 
    "type": "array:16"
   }
  ], 
  "name": "C1G2BlockWrite", 
  "typeNum": 347
 }, 
 {
  "fields": [
   {
    "name": "EnableCRC", 
    "type": "bool"
   }, 
   {
    "name": "EnablePCBits", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "C1G2EPCMemorySelector", 
  "typeNum": 348
 }, 
 {
  "fields": [
   {
    "name": "PC_Bits", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2_PC", 
  "typeNum": 12
 }, 
 {
  "fields": [
   {
    "name": "CRC", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2_CRC", 
  "typeNum": 11
 }, 
 {
  "fields": [
   {
    "name": "NumCollisionSlots", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NumEmptySlots", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2SingulationDetails", 
  "typeNum": 18
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2ReadResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "ReadData", 
    "type": "array:16"
   }
  ], 
  "name": "C1G2ReadOpSpecResult", 
  "typeNum": 349
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2WriteResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NumWordsWritten", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2WriteOpSpecResult", 
  "typeNum": 350
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2KillResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2KillOpSpecResult", 
  "typeNum": 351
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2LockResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2LockOpSpecResult", 
  "typeNum": 352
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2BlockEraseResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2BlockEraseOpSpecResult", 
  "typeNum": 353
 }, 
 {
  "fields": [
   {
    "enumeration": "C1G2BlockWriteResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "NumWordsWritten", 
    "type": "uintbe:16"
   }
  ], 
  "name": "C1G2BlockWriteOpSpecResult", 
  "typeNum": 354
 }
]
messages = [
 {
  "fields": [
   {
    "name": "VendorIdentifier", 
    "type": "uintbe:32"
   }, 
   {
    "name": "MessageSubtype", 
    "type": "uintbe:8"
   }, 
   {
    "format": "Hex", 
    "name": "Data", 
    "type": "bytesToEnd"
   }
  ], 
  "name": "CUSTOM_MESSAGE", 
  "typeNum": 1023
 }, 
 {
  "fields": [
   {
    "enumeration": "GetReaderCapabilitiesRequestedData", 
    "name": "RequestedData", 
    "type": "uintbe:8"
   }
  ], 
  "name": "GET_READER_CAPABILITIES", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1
 }, 
 {
  "name": "GET_READER_CAPABILITIES_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "GeneralDeviceCapabilities", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "LLRPCapabilities", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "RegulatoryCapabilities", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 11
 }, 
 {
  "name": "ADD_ROSPEC", 
  "parameters": [
   {
    "parameter": "ROSpec", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 20
 }, 
 {
  "name": "ADD_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 30
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "DELETE_ROSPEC", 
  "typeNum": 21
 }, 
 {
  "name": "DELETE_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 31
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "START_ROSPEC", 
  "typeNum": 22
 }, 
 {
  "name": "START_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 32
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "STOP_ROSPEC", 
  "typeNum": 23
 }, 
 {
  "name": "STOP_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 33
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ENABLE_ROSPEC", 
  "typeNum": 24
 }, 
 {
  "name": "ENABLE_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 34
 }, 
 {
  "fields": [
   {
    "name": "ROSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "DISABLE_ROSPEC", 
  "typeNum": 25
 }, 
 {
  "name": "DISABLE_ROSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 35
 }, 
 {
  "name": "GET_ROSPECS", 
  "typeNum": 26
 }, 
 {
  "name": "GET_ROSPECS_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "ROSpec", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 36
 }, 
 {
  "name": "ADD_ACCESSSPEC", 
  "parameters": [
   {
    "parameter": "AccessSpec", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 40
 }, 
 {
  "name": "ADD_ACCESSSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 50
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "DELETE_ACCESSSPEC", 
  "typeNum": 41
 }, 
 {
  "name": "DELETE_ACCESSSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 51
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ENABLE_ACCESSSPEC", 
  "typeNum": 42
 }, 
 {
  "name": "ENABLE_ACCESSSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 52
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "DISABLE_ACCESSSPEC", 
  "typeNum": 43
 }, 
 {
  "name": "DISABLE_ACCESSSPEC_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 53
 }, 
 {
  "name": "GET_ACCESSSPECS", 
  "typeNum": 44
 }, 
 {
  "name": "GET_ACCESSSPECS_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "AccessSpec", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 54
 }, 
 {
  "fields": [
   {
    "name": "AntennaID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "GetReaderConfigRequestedData", 
    "name": "RequestedData", 
    "type": "uintbe:8"
   }, 
   {
    "name": "GPIPortNum", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPOPortNum", 
    "type": "uintbe:16"
   }
  ], 
  "name": "GET_READER_CONFIG", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 2
 }, 
 {
  "name": "GET_READER_CONFIG_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "Identification", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AntennaProperties", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "AntennaConfiguration", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "ReaderEventNotificationSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ROReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AccessReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "LLRPConfigurationStateValue", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "KeepaliveSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "GPIPortCurrentState", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "GPOWriteData", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "EventsAndReports", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 12
 }, 
 {
  "fields": [
   {
    "name": "ResetToFactoryDefault", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "SET_READER_CONFIG", 
  "parameters": [
   {
    "parameter": "ReaderEventNotificationSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AntennaProperties", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "AntennaConfiguration", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "ROReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "AccessReportSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "KeepaliveSpec", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "GPOWriteData", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "GPIPortCurrentState", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "EventsAndReports", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 3
 }, 
 {
  "name": "SET_READER_CONFIG_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 13
 }, 
 {
  "name": "CLOSE_CONNECTION", 
  "typeNum": 14
 }, 
 {
  "name": "CLOSE_CONNECTION_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 4
 }, 
 {
  "name": "GET_REPORT", 
  "typeNum": 60
 }, 
 {
  "name": "RO_ACCESS_REPORT", 
  "parameters": [
   {
    "parameter": "TagReportData", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "RFSurveyReportData", 
    "repeat": [
     0, 
     99999
    ]
   }, 
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 61
 }, 
 {
  "name": "KEEPALIVE", 
  "typeNum": 62
 }, 
 {
  "name": "KEEPALIVE_ACK", 
  "typeNum": 72
 }, 
 {
  "name": "READER_EVENT_NOTIFICATION", 
  "parameters": [
   {
    "parameter": "ReaderEventNotificationData", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 63
 }, 
 {
  "name": "ENABLE_EVENTS_AND_REPORTS", 
  "typeNum": 64
 }, 
 {
  "name": "ERROR_MESSAGE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }
  ], 
  "typeNum": 100
 }
]
