#-----------------------------------------------------------
# DO NOT EDIT!
# MACHINE GENERATED from llrp-1x0-def.xml
#
# Created: 2013-12-03 22:39:18.248000 
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
 }, 
 {
  "choices": [
   [
    1000, 
    "All_Capabilities"
   ], 
   [
    1001, 
    "Impinj_Detailed_Version"
   ], 
   [
    1002, 
    "Impinj_Frequency_Capabilities"
   ], 
   [
    1003, 
    "Impinj_Array_Capabilities"
   ], 
   [
    2000, 
    "All_Configuration"
   ], 
   [
    2001, 
    "Impinj_Sub_Regulatory_Region"
   ], 
   [
    2002, 
    "Impinj_Forklift_Configuration"
   ], 
   [
    2003, 
    "Impinj_GPI_Debounce_Configuration"
   ], 
   [
    2004, 
    "Impinj_Reader_Temperature"
   ], 
   [
    2005, 
    "Impinj_Link_Monitor_Configuration"
   ], 
   [
    2006, 
    "Impinj_Report_Buffer_Configuration"
   ], 
   [
    2007, 
    "Impinj_Access_Spec_Configuration"
   ], 
   [
    2008, 
    "Impinj_GPS_NMEA_Sentences"
   ], 
   [
    2009, 
    "Impinj_Advanced_GPO_Configuration"
   ], 
   [
    2010, 
    "Impinj_Tilt_Configuration"
   ], 
   [
    2011, 
    "Impinj_Beacon_Configuration"
   ], 
   [
    2012, 
    "Impinj_Antenna_Configuration"
   ], 
   [
    2013, 
    "Impinj_Location_Configuration"
   ], 
   [
    2014, 
    "Impinj_Transition_Configuration"
   ]
  ], 
  "name": "ImpinjRequestedDataType"
 }, 
 {
  "choices": [
   [
    0, 
    "FCC_Part_15_247"
   ], 
   [
    1, 
    "ETSI_EN_300_220"
   ], 
   [
    2, 
    "ETSI_EN_302_208_With_LBT"
   ], 
   [
    3, 
    "Hong_Kong_920_925_MHz"
   ], 
   [
    4, 
    "Taiwan_922_928_MHz"
   ], 
   [
    5, 
    "Japan_952_954_MHz"
   ], 
   [
    6, 
    "Japan_952_954_MHz_Low_Power"
   ], 
   [
    7, 
    "ETSI_EN_302_208_v1_2_1"
   ], 
   [
    8, 
    "Korea_917_921_MHz"
   ], 
   [
    9, 
    "Malaysia_919_923_MHz"
   ], 
   [
    10, 
    "China_920_925_MHz"
   ], 
   [
    11, 
    "Japan_952_956_MHz_Without_LBT"
   ], 
   [
    12, 
    "South_Africa_915_919_MHz"
   ], 
   [
    13, 
    "Brazil_902_907_and_915_928_MHz"
   ], 
   [
    14, 
    "Thailand_920_925_MHz"
   ], 
   [
    15, 
    "Singapore_920_925_MHz"
   ], 
   [
    16, 
    "Australia_920_926_MHz"
   ], 
   [
    17, 
    "India_865_867_MHz"
   ], 
   [
    18, 
    "Uruguay_916_928_MHz"
   ], 
   [
    19, 
    "Vietnam_920_925_MHz"
   ], 
   [
    20, 
    "Israel_915_917_MHz"
   ], 
   [
    21, 
    "Philippines_918_920_MHz"
   ], 
   [
    22, 
    "Canada_Post"
   ], 
   [
    23, 
    "Indonesia_923_925_MHz"
   ], 
   [
    24, 
    "New_Zealand_921p5_928_MHz"
   ], 
   [
    25, 
    "Japan_916_921_MHz_Without_LBT"
   ], 
   [
    26, 
    "Latin_America_902_928_MHz"
   ]
  ], 
  "name": "ImpinjRegulatoryRegion"
 }, 
 {
  "choices": [
   [
    0, 
    "Reader_Selected"
   ], 
   [
    1, 
    "Single_Target"
   ], 
   [
    2, 
    "Dual_Target"
   ], 
   [
    3, 
    "Single_Target_With_Suppression"
   ]
  ], 
  "name": "ImpinjInventorySearchType"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Auto_Select"
   ], 
   [
    2, 
    "Channel_List"
   ]
  ], 
  "name": "ImpinjFixedFrequencyMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjReducedPowerMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjLowDutyCycleMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjLinkMonitorMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Normal"
   ], 
   [
    1, 
    "Low_Latency"
   ]
  ], 
  "name": "ImpinjReportBufferMode"
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
   ], 
   [
    5, 
    "Incorrect_Password_Error"
   ], 
   [
    6, 
    "Tag_Memory_Overrun_Error"
   ]
  ], 
  "name": "ImpinjBlockPermalockResultType"
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
   ], 
   [
    4, 
    "Incorrect_Password_Error"
   ], 
   [
    5, 
    "Tag_Memory_Overrun_Error"
   ]
  ], 
  "name": "ImpinjGetBlockPermalockStatusResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Unknown"
   ], 
   [
    1, 
    "Private"
   ], 
   [
    2, 
    "Public"
   ]
  ], 
  "name": "ImpinjQTDataProfile"
 }, 
 {
  "choices": [
   [
    0, 
    "Unknown"
   ], 
   [
    1, 
    "Normal_Range"
   ], 
   [
    2, 
    "Short_Range"
   ]
  ], 
  "name": "ImpinjQTAccessRange"
 }, 
 {
  "choices": [
   [
    0, 
    "Unknown"
   ], 
   [
    1, 
    "Temporary"
   ], 
   [
    2, 
    "Permanent"
   ]
  ], 
  "name": "ImpinjQTPersistence"
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
   ], 
   [
    5, 
    "Incorrect_Password_Error"
   ]
  ], 
  "name": "ImpinjSetQTConfigResultType"
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
   ], 
   [
    4, 
    "Incorrect_Password_Error"
   ]
  ], 
  "name": "ImpinjGetQTConfigResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjSerializedTIDMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjRFPhaseAngleMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjPeakRSSIMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjGPSCoordinatesMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Normal"
   ], 
   [
    1, 
    "Pulsed"
   ], 
   [
    2, 
    "Reader_Operational_Status"
   ], 
   [
    3, 
    "LLRP_Connection_Status"
   ], 
   [
    4, 
    "Reader_Inventory_Status"
   ], 
   [
    5, 
    "Network_Connection_Status"
   ], 
   [
    6, 
    "Reader_Inventory_Tags_Status"
   ]
  ], 
  "name": "ImpinjAdvancedGPOMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjOptimizedReadMode"
 }, 
 {
  "choices": [
   [
    0, 
    "FIFO"
   ], 
   [
    1, 
    "Ascending"
   ]
  ], 
  "name": "ImpinjAccessSpecOrderingMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjRFDopplerFrequencyMode"
 }, 
 {
  "choices": [
   [
    0, 
    "Disabled"
   ], 
   [
    1, 
    "Enabled"
   ]
  ], 
  "name": "ImpinjEncodeStatus"
 }, 
 {
  "choices": [
   [
    0, 
    "No_Action"
   ], 
   [
    1, 
    "Unlock"
   ], 
   [
    2, 
    "Lock"
   ], 
   [
    3, 
    "Perma_Lock"
   ], 
   [
    4, 
    "Perma_Unlock"
   ]
  ], 
  "name": "ImpinjLockPrivilege"
 }, 
 {
  "choices": [
   [
    1, 
    "Batch"
   ], 
   [
    2, 
    "Continuous"
   ]
  ], 
  "name": "ImpinjEncodeMode"
 }, 
 {
  "choices": [
   [
    1, 
    "Monza3"
   ], 
   [
    2, 
    "Monza4"
   ], 
   [
    3, 
    "Monza5"
   ], 
   [
    100, 
    "AnyGen2"
   ]
  ], 
  "name": "ImpinjTagICType"
 }, 
 {
  "choices": [
   [
    1, 
    "Op_Spec_Started"
   ], 
   [
    2, 
    "Op_Spec_Finished"
   ], 
   [
    3, 
    "Op_Spec_Success"
   ], 
   [
    4, 
    "Op_Spec_Failure"
   ], 
   [
    5, 
    "Op_Spec_SingleSuccess"
   ], 
   [
    6, 
    "Op_Spec_SingleFailure"
   ]
  ], 
  "name": "ImpinjOpSpecAction"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Success_With_Degraded_Performance"
   ], 
   [
    2, 
    "Encode_Timeout"
   ], 
   [
    3, 
    "Encode_Data_Cache_Empty"
   ], 
   [
    4, 
    "Wrong_Tag_IC_Detected"
   ]
  ], 
  "name": "ImpinjEncodeResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Success"
   ], 
   [
    1, 
    "Failure"
   ], 
   [
    2, 
    "Timeout"
   ], 
   [
    3, 
    "Not_Attempted"
   ], 
   [
    4, 
    "Insufficient_Power"
   ], 
   [
    5, 
    "No_Response_From_Tag"
   ], 
   [
    6, 
    "Incorrect_Password_Error"
   ], 
   [
    7, 
    "Tag_Memory_Locked_Error"
   ], 
   [
    8, 
    "Nonspecific_Tag_Error"
   ], 
   [
    9, 
    "Nonspecific_Reader_Error"
   ]
  ], 
  "name": "ImpinjEncodeDataResultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Unknown"
   ], 
   [
    1, 
    "Disconnected"
   ], 
   [
    2, 
    "Connected"
   ]
  ], 
  "name": "ImpinjHubConnectedType"
 }, 
 {
  "choices": [
   [
    0, 
    "No_Fault"
   ], 
   [
    1, 
    "RF_Power"
   ], 
   [
    2, 
    "RF_Power_On_Hub_1"
   ], 
   [
    3, 
    "RF_Power_On_Hub_2"
   ], 
   [
    4, 
    "RF_Power_On_Hub_3"
   ], 
   [
    5, 
    "RF_Power_On_Hub_4"
   ], 
   [
    6, 
    "No_Init"
   ], 
   [
    7, 
    "Serial_Overflow"
   ], 
   [
    8, 
    "Disconnected"
   ]
  ], 
  "name": "ImpinjHubFaultType"
 }, 
 {
  "choices": [
   [
    0, 
    "Entry"
   ], 
   [
    1, 
    "Update"
   ], 
   [
    2, 
    "Exit"
   ]
  ], 
  "name": "ImpinjLocationReportType"
 }, 
 {
  "choices": [
   [
    0, 
    "Standard"
   ], 
   [
    1, 
    "Large"
   ]
  ], 
  "name": "ImpinjTransitionZoneRange"
 }, 
 {
  "choices": [
   [
    0, 
    "NewTag"
   ], 
   [
    1, 
    "StrayTag"
   ], 
   [
    2, 
    "TagTransition"
   ]
  ], 
  "name": "ImpinjZoneReportType"
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
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjRequestedDataType", 
    "name": "RequestedData", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjRequestedData", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 21
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjRegulatoryRegion", 
    "name": "RegulatoryRegion", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjSubRegulatoryRegion", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 22
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjInventorySearchType", 
    "name": "InventorySearchMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjInventorySearchMode", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 23
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjFixedFrequencyMode", 
    "name": "FixedFrequencyMode", 
    "type": "uintbe:16"
   }, 
   {
    "name": "skip:16", 
    "type": "skip:16"
   }, 
   {
    "name": "ChannelList", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjFixedFrequencyList", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 26
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjReducedPowerMode", 
    "name": "ReducedPowerMode", 
    "type": "uintbe:16"
   }, 
   {
    "name": "skip:16", 
    "type": "skip:16"
   }, 
   {
    "name": "ChannelList", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjReducedPowerFrequencyList", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 27
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjLowDutyCycleMode", 
    "name": "LowDutyCycleMode", 
    "type": "uintbe:16"
   }, 
   {
    "name": "EmptyFieldTimeout", 
    "type": "uintbe:16"
   }, 
   {
    "name": "FieldPingInterval", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjLowDutyCycle", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 28
 }, 
 {
  "name": "ImpinjHubVersions", 
  "parameters": [
   {
    "parameter": "ImpinjArrayVersion", 
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
  "typeNum": 1537
 }, 
 {
  "fields": [
   {
    "name": "ModelName", 
    "type": "string"
   }, 
   {
    "name": "SerialNumber", 
    "type": "string"
   }, 
   {
    "name": "SoftwareVersion", 
    "type": "string"
   }, 
   {
    "name": "FirmwareVersion", 
    "type": "string"
   }, 
   {
    "name": "FPGAVersion", 
    "type": "string"
   }, 
   {
    "name": "PCBAVersion", 
    "type": "string"
   }
  ], 
  "name": "ImpinjDetailedVersion", 
  "parameters": [
   {
    "parameter": "ImpinjHubVersions", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjArrayVersion", 
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
  "typeNum": 29
 }, 
 {
  "fields": [
   {
    "name": "FrequencyList", 
    "type": "array:32"
   }
  ], 
  "name": "ImpinjFrequencyCapabilities", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 30
 }, 
 {
  "name": "ImpinjForkliftConfiguration", 
  "parameters": [
   {
    "parameter": "ImpinjForkliftHeightThreshold", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjForkliftZeroMotionTimeThreshold", 
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
  "typeNum": 32
 }, 
 {
  "fields": [
   {
    "name": "HeightThreshold", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjForkliftHeightThreshold", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 33
 }, 
 {
  "fields": [
   {
    "name": "ZeroMotionTimeThreshold", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjForkliftZeroMotionTimeThreshold", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 34
 }, 
 {
  "fields": [
   {
    "name": "BoardManufacturer", 
    "type": "string"
   }, 
   {
    "format": "Hex", 
    "name": "FirmwareVersion", 
    "type": "array:8"
   }, 
   {
    "format": "Hex", 
    "name": "HardwareVersion", 
    "type": "array:8"
   }
  ], 
  "name": "ImpinjForkliftCompanionBoardInfo", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 35
 }, 
 {
  "fields": [
   {
    "name": "GPIPortNum", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPIDebounceTimerMSec", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjGPIDebounceConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 36
 }, 
 {
  "fields": [
   {
    "name": "Temperature", 
    "type": "intbe:16"
   }
  ], 
  "name": "ImpinjReaderTemperature", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 37
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjLinkMonitorMode", 
    "name": "LinkMonitorMode", 
    "type": "uintbe:16"
   }, 
   {
    "name": "LinkDownThreshold", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjLinkMonitorConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 38
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjReportBufferMode", 
    "name": "ReportBufferMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjReportBufferConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 39
 }, 
 {
  "name": "ImpinjAccessSpecConfiguration", 
  "parameters": [
   {
    "parameter": "ImpinjBlockWriteWordCount", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjOpSpecRetryCount", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjAccessSpecOrdering", 
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
  "typeNum": 40
 }, 
 {
  "fields": [
   {
    "name": "WordCount", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjBlockWriteWordCount", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 41
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
    "name": "BlockPointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "BlockMask", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjBlockPermalock", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 42
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjBlockPermalockResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjBlockPermalockOpSpecResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 43
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
    "name": "BlockPointer", 
    "type": "uintbe:16"
   }, 
   {
    "name": "BlockRange", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjGetBlockPermalockStatus", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 44
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjGetBlockPermalockStatusResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "PermalockStatus", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjGetBlockPermalockStatusOpSpecResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 45
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
    "enumeration": "ImpinjQTDataProfile", 
    "name": "DataProfile", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjQTAccessRange", 
    "name": "AccessRange", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjQTPersistence", 
    "name": "Persistence", 
    "type": "uintbe:8"
   }, 
   {
    "name": "skip:32", 
    "type": "skip:32"
   }
  ], 
  "name": "ImpinjSetQTConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 46
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjSetQTConfigResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjSetQTConfigOpSpecResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 47
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
  "name": "ImpinjGetQTConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 48
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjGetQTConfigResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjQTDataProfile", 
    "name": "DataProfile", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjQTAccessRange", 
    "name": "AccessRange", 
    "type": "uintbe:8"
   }, 
   {
    "name": "skip:32", 
    "type": "skip:32"
   }
  ], 
  "name": "ImpinjGetQTConfigOpSpecResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 49
 }, 
 {
  "name": "ImpinjTagReportContentSelector", 
  "parameters": [
   {
    "parameter": "ImpinjEnableSerializedTID", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEnableRFPhaseAngle", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEnablePeakRSSI", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEnableGPSCoordinates", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEnableOptimizedRead", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEnableRFDopplerFrequency", 
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
  "typeNum": 50
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjSerializedTIDMode", 
    "name": "SerializedTIDMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnableSerializedTID", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 51
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjRFPhaseAngleMode", 
    "name": "RFPhaseAngleMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnableRFPhaseAngle", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 52
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjPeakRSSIMode", 
    "name": "PeakRSSIMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnablePeakRSSI", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 53
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjGPSCoordinatesMode", 
    "name": "GPSCoordinatesMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnableGPSCoordinates", 
  "parameters": [
   {
    "parameter": "Custom", 
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
    "format": "Hex", 
    "name": "TID", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjSerializedTID", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 55
 }, 
 {
  "fields": [
   {
    "name": "PhaseAngle", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjRFPhaseAngle", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 56
 }, 
 {
  "fields": [
   {
    "name": "RSSI", 
    "type": "intbe:16"
   }
  ], 
  "name": "ImpinjPeakRSSI", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 57
 }, 
 {
  "fields": [
   {
    "name": "Latitude", 
    "type": "intbe:32"
   }, 
   {
    "name": "Longitude", 
    "type": "intbe:32"
   }
  ], 
  "name": "ImpinjGPSCoordinates", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 58
 }, 
 {
  "fields": [
   {
    "name": "LoopCount", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjLoopSpec", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 59
 }, 
 {
  "name": "ImpinjGPSNMEASentences", 
  "parameters": [
   {
    "parameter": "ImpinjGGASentence", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjRMCSentence", 
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
  "typeNum": 60
 }, 
 {
  "fields": [
   {
    "name": "GGASentence", 
    "type": "string"
   }
  ], 
  "name": "ImpinjGGASentence", 
  "parameters": [
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
  "fields": [
   {
    "name": "RMCSentence", 
    "type": "string"
   }
  ], 
  "name": "ImpinjRMCSentence", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 62
 }, 
 {
  "fields": [
   {
    "name": "RetryCount", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjOpSpecRetryCount", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 63
 }, 
 {
  "fields": [
   {
    "name": "GPOPortNum", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjAdvancedGPOMode", 
    "name": "GPOMode", 
    "type": "uintbe:16"
   }, 
   {
    "name": "GPOPulseDurationMSec", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjAdvancedGPOConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 64
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjOptimizedReadMode", 
    "name": "OptimizedReadMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnableOptimizedRead", 
  "parameters": [
   {
    "parameter": "C1G2Read", 
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
  "typeNum": 65
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjAccessSpecOrderingMode", 
    "name": "OrderingMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjAccessSpecOrdering", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 66
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjRFDopplerFrequencyMode", 
    "name": "RFDopplerFrequencyMode", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEnableRFDopplerFrequency", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 67
 }, 
 {
  "fields": [
   {
    "name": "DopplerFrequency", 
    "type": "intbe:16"
   }
  ], 
  "name": "ImpinjRFDopplerFrequency", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 68
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjEncodeStatus", 
    "name": "EncodeStatus", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjSTPCapabilities", 
  "parameters": [
   {
    "parameter": "ImpinjTagIC", 
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
  "typeNum": 1501
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjTagICType", 
    "name": "Type", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjTagIC", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1502
 }, 
 {
  "fields": [
   {
    "name": "EncodeDataCacheID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "LowEncodeDataThreshold", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEncodeDataCache", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeDataDefaults", 
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
  "typeNum": 1503
 }, 
 {
  "name": "ImpinjEncodeDataDefaults", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeDataPCBits", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataAccessPassword", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataKillPassword", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataUserMemory", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataAlternateEPC", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataQTConfig", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataLockConfig", 
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
  "typeNum": 1504
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "EPC", 
    "type": "bitarray"
   }
  ], 
  "name": "ImpinjEncodeData", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeDataPCBits", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataAccessPassword", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataKillPassword", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataUserMemory", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataAlternateEPC", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataQTConfig", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataLockConfig", 
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
  "typeNum": 1505
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "PCBits", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEncodeDataPCBits", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1506
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjEncodeDataAccessPassword", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1507
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "KillPassword", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjEncodeDataKillPassword", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1508
 }, 
 {
  "fields": [
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
  "name": "ImpinjEncodeDataUserMemory", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1509
 }, 
 {
  "fields": [
   {
    "format": "Hex", 
    "name": "AlternateEPC", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjEncodeDataAlternateEPC", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1510
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjQTDataProfile", 
    "name": "DataProfile", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjQTAccessRange", 
    "name": "AccessRange", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjQTPersistence", 
    "name": "Persistence", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ImpinjEncodeDataQTConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1511
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjLockPrivilege", 
    "name": "AccessPasswordLock", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjLockPrivilege", 
    "name": "KillPasswordLock", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjLockPrivilege", 
    "name": "EPCMemoryLock", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjLockPrivilege", 
    "name": "TIDMemoryLock", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjLockPrivilege", 
    "name": "UserMemoryLock", 
    "type": "uintbe:8"
   }, 
   {
    "name": "UserBlockPermalockPointer", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "UserBlockPermalockMask", 
    "type": "array:16"
   }
  ], 
  "name": "ImpinjEncodeDataLockConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1512
 }, 
 {
  "fields": [
   {
    "name": "EncodeDataCacheID", 
    "type": "uintbe:32"
   }, 
   {
    "name": "Threshold", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Count", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjLowEncodeDataThresholdEvent", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1513
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "format": "Hex", 
    "name": "AccessPassword", 
    "type": "uintbe:32"
   }, 
   {
    "name": "EncodeDataCacheID", 
    "type": "uintbe:32"
   }, 
   {
    "enumeration": "ImpinjEncodeMode", 
    "name": "Mode", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjTagICType", 
    "name": "TagIC", 
    "type": "uintbe:16"
   }, 
   {
    "name": "EncodeCount", 
    "type": "uintbe:32"
   }, 
   {
    "name": "TagsInViewCount", 
    "type": "uintbe:16"
   }, 
   {
    "name": "EncodeReportCount", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TagInViewTimeout", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjEncodeOpSpec", 
  "parameters": [
   {
    "parameter": "ImpinjOpSpecGPOPulse", 
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
  "typeNum": 1514
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjOpSpecAction", 
    "name": "OpSpecAction", 
    "type": "uintbe:16"
   }, 
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
   }, 
   {
    "name": "GPOPulseDurationMSec", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjOpSpecGPOPulse", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1515
 }, 
 {
  "fields": [
   {
    "name": "AccessSpecID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjEncodeReportData", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeOpSpecResult", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataResult", 
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
  "typeNum": 1516
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjEncodeResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }, 
   {
    "name": "ElapsedTime", 
    "type": "uintbe:64"
   }, 
   {
    "name": "AttemptCount", 
    "type": "uintbe:32"
   }, 
   {
    "name": "SuccessCount", 
    "type": "uintbe:32"
   }
  ], 
  "name": "ImpinjEncodeOpSpecResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1517
 }, 
 {
  "fields": [
   {
    "name": "OpSpecID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "Result", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ImpinjEncodeDataResult", 
  "parameters": [
   {
    "parameter": "EPCData", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataDetailedResult", 
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
  "typeNum": 1518
 }, 
 {
  "fields": [
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeEPCResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodePCBitsResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeAccessPasswordResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeKillPasswordResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeUserMemoryResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeAlternateEPCResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeQTConfigResult", 
    "type": "uintbe:8"
   }, 
   {
    "enumeration": "ImpinjEncodeDataResultType", 
    "name": "EncodeLockConfigResult", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ImpinjEncodeDataDetailedResult", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1519
 }, 
 {
  "fields": [
   {
    "name": "SerialNumber", 
    "type": "string"
   }, 
   {
    "name": "FirmwareVersion", 
    "type": "string"
   }, 
   {
    "name": "PCBAVersion", 
    "type": "string"
   }
  ], 
  "name": "ImpinjArrayVersion", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1520
 }, 
 {
  "fields": [
   {
    "name": "MaxNumSectors", 
    "type": "uintbe:32"
   }, 
   {
    "name": "SupportsLISpecs", 
    "type": "bool"
   }, 
   {
    "name": "SupportsDISpecs", 
    "type": "bool"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "ImpinjArrayCapabilities", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1521
 }, 
 {
  "fields": [
   {
    "name": "XAxis", 
    "type": "intbe:32"
   }, 
   {
    "name": "YAxis", 
    "type": "intbe:32"
   }, 
   {
    "name": "ZAxis", 
    "type": "intbe:32"
   }
  ], 
  "name": "ImpinjTiltConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1522
 }, 
 {
  "fields": [
   {
    "name": "BeaconState", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }, 
   {
    "name": "BeaconDuration", 
    "type": "uintbe:64"
   }
  ], 
  "name": "ImpinjBeaconConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1523
 }, 
 {
  "name": "ImpinjAntennaConfiguration", 
  "parameters": [
   {
    "parameter": "ImpinjAntennaEventHysteresis", 
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
  "typeNum": 1524
 }, 
 {
  "fields": [
   {
    "name": "AntennaEventConnected", 
    "type": "uintbe:64"
   }, 
   {
    "name": "AntennaEventDisconnected", 
    "type": "uintbe:64"
   }
  ], 
  "name": "ImpinjAntennaEventHysteresis", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1526
 }, 
 {
  "name": "ImpinjTagReporting", 
  "parameters": [
   {
    "parameter": "ImpinjEnableTagReport", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjAllowStaleTags", 
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
  "typeNum": 1534
 }, 
 {
  "fields": [
   {
    "name": "TagMode", 
    "type": "bool"
   }, 
   {
    "name": "skip:15", 
    "type": "skip:15"
   }
  ], 
  "name": "ImpinjEnableTagReport", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1535
 }, 
 {
  "fields": [
   {
    "name": "Allow", 
    "type": "bool"
   }, 
   {
    "name": "skip:15", 
    "type": "skip:15"
   }
  ], 
  "name": "ImpinjAllowStaleTags", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1536
 }, 
 {
  "fields": [
   {
    "name": "HubID", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjHubConnectedType", 
    "name": "Connected", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjHubFaultType", 
    "name": "Fault", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjHubConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1538
 }, 
 {
  "fields": [
   {
    "name": "Metric", 
    "type": "array:32"
   }
  ], 
  "name": "ImpinjArrayReportMetric", 
  "typeNum": 1539
 }, 
 {
  "fields": [
   {
    "name": "HeightCm", 
    "type": "intbe:16"
   }, 
   {
    "name": "FacilityXLocationCm", 
    "type": "intbe:32"
   }, 
   {
    "name": "FacilityYLocationCm", 
    "type": "intbe:32"
   }, 
   {
    "name": "OrientationDegrees", 
    "type": "intbe:16"
   }
  ], 
  "name": "ImpinjPlacementConfiguration", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1540
 }, 
 {
  "name": "ImpinjLISpec", 
  "parameters": [
   {
    "parameter": "ImpinjLocationConfig", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjC1G2LocationConfig", 
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
  "typeNum": 1541
 }, 
 {
  "fields": [
   {
    "name": "MotionWindowSeconds", 
    "type": "uintbe:8"
   }, 
   {
    "name": "TagAgeIntervalSeconds", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjLocationConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1542
 }, 
 {
  "fields": [
   {
    "name": "ModeIndex", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Session", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:6", 
    "type": "skip:6"
   }
  ], 
  "name": "ImpinjC1G2LocationConfig", 
  "parameters": [
   {
    "parameter": "C1G2Filter", 
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
  "typeNum": 1543
 }, 
 {
  "fields": [
   {
    "name": "ReportIntervalSeconds", 
    "type": "uintbe:16"
   }, 
   {
    "name": "EnableLocationUpdateReport", 
    "type": "bool"
   }, 
   {
    "name": "EnableLocationEntryReport", 
    "type": "bool"
   }, 
   {
    "name": "EnableLocationExitReport", 
    "type": "bool"
   }, 
   {
    "name": "skip:5", 
    "type": "skip:5"
   }
  ], 
  "name": "ImpinjLocationReporting", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1544
 }, 
 {
  "fields": [
   {
    "name": "TimestampUTC", 
    "type": "uintbe:64"
   }, 
   {
    "name": "LocXCentimeters", 
    "type": "intbe:32"
   }, 
   {
    "name": "LocYCentimeters", 
    "type": "intbe:32"
   }, 
   {
    "name": "Confidence", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjLocationReportType", 
    "name": "Type", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ImpinjLocationReportData", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1545
 }, 
 {
  "fields": [
   {
    "name": "SectorID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjSectorID", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1528
 }, 
 {
  "fields": [
   {
    "name": "SectorID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TransmitPower", 
    "type": "intbe:32"
   }, 
   {
    "name": "ReceiverSensitivity", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjSectorConfiguration", 
  "parameters": [
   {
    "parameter": "ImpinjFixedFrequencyList", 
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
  "typeNum": 1525
 }, 
 {
  "fields": [
   {
    "name": "SectorIDs", 
    "type": "array:16"
   }, 
   {
    "name": "ZoneID", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjTransitionZone", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1546
 }, 
 {
  "name": "ImpinjTISpec", 
  "parameters": [
   {
    "parameter": "ImpinjTransitionZone", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "ImpinjTransitionConfig", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjC1G2TransitionConfig", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjSectorConfiguration", 
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
  "typeNum": 1547
 }, 
 {
  "fields": [
   {
    "name": "InitialStraySearchTimeSec", 
    "type": "uintbe:16"
   }, 
   {
    "name": "StrayUpdateIntervalSec", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjTransitionZoneRange", 
    "name": "TransitionZoneRange", 
    "type": "uintbe:8"
   }, 
   {
    "name": "TOITagAgeSec", 
    "type": "uintbe:16"
   }, 
   {
    "name": "StrayTagAgeSec", 
    "type": "uintbe:16"
   }
  ], 
  "name": "ImpinjTransitionConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1548
 }, 
 {
  "fields": [
   {
    "name": "ModeIndex", 
    "type": "uintbe:16"
   }, 
   {
    "name": "TOISession", 
    "type": "bits:2"
   }, 
   {
    "name": "StraySession", 
    "type": "bits:2"
   }, 
   {
    "name": "skip:4", 
    "type": "skip:4"
   }
  ], 
  "name": "ImpinjC1G2TransitionConfig", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1549
 }, 
 {
  "fields": [
   {
    "name": "ImpinjEnableTransitionReport", 
    "type": "bool"
   }, 
   {
    "name": "ImpinjEnableStrayReport", 
    "type": "bool"
   }, 
   {
    "name": "ImpinjEnableEntryReport", 
    "type": "bool"
   }, 
   {
    "name": "skip:5", 
    "type": "skip:5"
   }
  ], 
  "name": "ImpinjTransitionReporting", 
  "typeNum": 1550
 }, 
 {
  "fields": [
   {
    "name": "TimestampUTC", 
    "type": "uintbe:64"
   }, 
   {
    "name": "FromZoneID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "ToZoneID", 
    "type": "uintbe:16"
   }, 
   {
    "name": "Confidence", 
    "type": "uintbe:16"
   }, 
   {
    "enumeration": "ImpinjZoneReportType", 
    "name": "ReportType", 
    "type": "uintbe:8"
   }
  ], 
  "name": "ImpinjTransitionReportData", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 1551
 }, 
 {
  "name": "ImpinjExtendedTagInformation", 
  "parameters": [
   {
    "parameter": "EPCData", 
    "repeat": [
     1, 
     99999
    ]
   }, 
   {
    "parameter": "ImpinjTransitionReportData", 
    "repeat": [
     0, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjLocationReportData", 
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
  "typeNum": 1552
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
 }, 
 {
  "fields": [
   {
    "name": "skip:32", 
    "type": "skip:32"
   }
  ], 
  "name": "IMPINJ_ENABLE_EXTENSIONS", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 21
 }, 
 {
  "name": "IMPINJ_ENABLE_EXTENSIONS_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
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
  "typeNum": 22
 }, 
 {
  "fields": [
   {
    "name": "SaveConfiguration", 
    "type": "bool"
   }, 
   {
    "name": "skip:7", 
    "type": "skip:7"
   }
  ], 
  "name": "IMPINJ_SAVE_SETTINGS", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 23
 }, 
 {
  "name": "IMPINJ_SAVE_SETTINGS_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
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
  "typeNum": 24
 }, 
 {
  "name": "IMPINJ_ADD_ENCODE_DATA_CACHE", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeDataCache", 
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
  "typeNum": 150
 }, 
 {
  "name": "IMPINJ_ADD_ENCODE_DATA_CACHE_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
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
  "typeNum": 151
 }, 
 {
  "fields": [
   {
    "name": "EncodeDataCacheID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "IMPINJ_DELETE_ENCODE_DATA_CACHE", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 152
 }, 
 {
  "name": "IMPINJ_DELETE_ENCODE_DATA_CACHE_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
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
  "typeNum": 153
 }, 
 {
  "name": "IMPINJ_GET_ENCODE_DATA_CACHES", 
  "parameters": [
   {
    "parameter": "Custom", 
    "repeat": [
     0, 
     99999
    ]
   }
  ], 
  "typeNum": 154
 }, 
 {
  "name": "IMPINJ_GET_ENCODE_DATA_CACHES_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
    "repeat": [
     1, 
     1
    ]
   }, 
   {
    "parameter": "ImpinjEncodeDataCache", 
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
  "typeNum": 155
 }, 
 {
  "fields": [
   {
    "name": "EncodeDataCacheID", 
    "type": "uintbe:32"
   }
  ], 
  "name": "IMPINJ_ADD_ENCODE_DATA", 
  "parameters": [
   {
    "parameter": "ImpinjEncodeData", 
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
  "typeNum": 156
 }, 
 {
  "name": "IMPINJ_ADD_ENCODE_DATA_RESPONSE", 
  "parameters": [
   {
    "parameter": "LLRPStatus", 
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
  "typeNum": 157
 }
]
