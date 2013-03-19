
#---------------------------------------------------------------------------
# AirProtocols
#
AirProtocols_Unspecified = 0
AirProtocols_EPCGlobalClass1Gen2 = 1

#---------------------------------------------------------------------------
# GetReaderCapabilitiesRequestedData
#
GetReaderCapabilitiesRequestedData_All = 0
GetReaderCapabilitiesRequestedData_General_Device_Capabilities = 1
GetReaderCapabilitiesRequestedData_LLRP_Capabilities = 2
GetReaderCapabilitiesRequestedData_Regulatory_Capabilities = 3
GetReaderCapabilitiesRequestedData_LLRP_Air_Protocol_Capabilities = 4

#---------------------------------------------------------------------------
# CommunicationsStandard
#
CommunicationsStandard_Unspecified = 0
CommunicationsStandard_US_FCC_Part_15 = 1
CommunicationsStandard_ETSI_302_208 = 2
CommunicationsStandard_ETSI_300_220 = 3
CommunicationsStandard_Australia_LIPD_1W = 4
CommunicationsStandard_Australia_LIPD_4W = 5
CommunicationsStandard_Japan_ARIB_STD_T89 = 6
CommunicationsStandard_Hong_Kong_OFTA_1049 = 7
CommunicationsStandard_Taiwan_DGT_LP0002 = 8
CommunicationsStandard_Korea_MIC_Article_5_2 = 9

#---------------------------------------------------------------------------
# ROSpecState
#
ROSpecState_Disabled = 0
ROSpecState_Inactive = 1
ROSpecState_Active = 2

#---------------------------------------------------------------------------
# ROSpecStartTriggerType
#
ROSpecStartTriggerType_Null = 0
ROSpecStartTriggerType_Immediate = 1
ROSpecStartTriggerType_Periodic = 2
ROSpecStartTriggerType_GPI = 3

#---------------------------------------------------------------------------
# ROSpecStopTriggerType
#
ROSpecStopTriggerType_Null = 0
ROSpecStopTriggerType_Duration = 1
ROSpecStopTriggerType_GPI_With_Timeout = 2

#---------------------------------------------------------------------------
# AISpecStopTriggerType
#
AISpecStopTriggerType_Null = 0
AISpecStopTriggerType_Duration = 1
AISpecStopTriggerType_GPI_With_Timeout = 2
AISpecStopTriggerType_Tag_Observation = 3

#---------------------------------------------------------------------------
# TagObservationTriggerType
#
TagObservationTriggerType_Upon_Seeing_N_Tags_Or_Timeout = 0
TagObservationTriggerType_Upon_Seeing_No_More_New_Tags_For_Tms_Or_Timeout = 1
TagObservationTriggerType_N_Attempts_To_See_All_Tags_In_FOV_Or_Timeout = 2

#---------------------------------------------------------------------------
# RFSurveySpecStopTriggerType
#
RFSurveySpecStopTriggerType_Null = 0
RFSurveySpecStopTriggerType_Duration = 1
RFSurveySpecStopTriggerType_N_Iterations_Through_Frequency_Range = 2

#---------------------------------------------------------------------------
# AccessSpecState
#
AccessSpecState_Disabled = 0
AccessSpecState_Active = 1

#---------------------------------------------------------------------------
# AccessSpecStopTriggerType
#
AccessSpecStopTriggerType_Null = 0
AccessSpecStopTriggerType_Operation_Count = 1

#---------------------------------------------------------------------------
# GetReaderConfigRequestedData
#
GetReaderConfigRequestedData_All = 0
GetReaderConfigRequestedData_Identification = 1
GetReaderConfigRequestedData_AntennaProperties = 2
GetReaderConfigRequestedData_AntennaConfiguration = 3
GetReaderConfigRequestedData_ROReportSpec = 4
GetReaderConfigRequestedData_ReaderEventNotificationSpec = 5
GetReaderConfigRequestedData_AccessReportSpec = 6
GetReaderConfigRequestedData_LLRPConfigurationStateValue = 7
GetReaderConfigRequestedData_KeepaliveSpec = 8
GetReaderConfigRequestedData_GPIPortCurrentState = 9
GetReaderConfigRequestedData_GPOWriteData = 10
GetReaderConfigRequestedData_EventsAndReports = 11

#---------------------------------------------------------------------------
# IdentificationType
#
IdentificationType_MAC_Address = 0
IdentificationType_EPC = 1

#---------------------------------------------------------------------------
# KeepaliveTriggerType
#
KeepaliveTriggerType_Null = 0
KeepaliveTriggerType_Periodic = 1

#---------------------------------------------------------------------------
# GPIPortState
#
GPIPortState_Low = 0
GPIPortState_High = 1
GPIPortState_Unknown = 2

#---------------------------------------------------------------------------
# ROReportTriggerType
#
ROReportTriggerType_None = 0
ROReportTriggerType_Upon_N_Tags_Or_End_Of_AISpec = 1
ROReportTriggerType_Upon_N_Tags_Or_End_Of_ROSpec = 2

#---------------------------------------------------------------------------
# AccessReportTriggerType
#
AccessReportTriggerType_Whenever_ROReport_Is_Generated = 0
AccessReportTriggerType_End_Of_AccessSpec = 1

#---------------------------------------------------------------------------
# NotificationEventType
#
NotificationEventType_Upon_Hopping_To_Next_Channel = 0
NotificationEventType_GPI_Event = 1
NotificationEventType_ROSpec_Event = 2
NotificationEventType_Report_Buffer_Fill_Warning = 3
NotificationEventType_Reader_Exception_Event = 4
NotificationEventType_RFSurvey_Event = 5
NotificationEventType_AISpec_Event = 6
NotificationEventType_AISpec_Event_With_Details = 7
NotificationEventType_Antenna_Event = 8

#---------------------------------------------------------------------------
# ROSpecEventType
#
ROSpecEventType_Start_Of_ROSpec = 0
ROSpecEventType_End_Of_ROSpec = 1
ROSpecEventType_Preemption_Of_ROSpec = 2

#---------------------------------------------------------------------------
# RFSurveyEventType
#
RFSurveyEventType_Start_Of_RFSurvey = 0
RFSurveyEventType_End_Of_RFSurvey = 1

#---------------------------------------------------------------------------
# AISpecEventType
#
AISpecEventType_End_Of_AISpec = 0

#---------------------------------------------------------------------------
# AntennaEventType
#
AntennaEventType_Antenna_Disconnected = 0
AntennaEventType_Antenna_Connected = 1

#---------------------------------------------------------------------------
# ConnectionAttemptStatusType
#
ConnectionAttemptStatusType_Success = 0
ConnectionAttemptStatusType_Failed_A_Reader_Initiated_Connection_Already_Exists = 1
ConnectionAttemptStatusType_Failed_A_Client_Initiated_Connection_Already_Exists = 2
ConnectionAttemptStatusType_Failed_Reason_Other_Than_A_Connection_Already_Exists = 3
ConnectionAttemptStatusType_Another_Connection_Attempted = 4

#---------------------------------------------------------------------------
# StatusCode
#
StatusCode_M_Success = 0
StatusCode_M_ParameterError = 100
StatusCode_M_FieldError = 101
StatusCode_M_UnexpectedParameter = 102
StatusCode_M_MissingParameter = 103
StatusCode_M_DuplicateParameter = 104
StatusCode_M_OverflowParameter = 105
StatusCode_M_OverflowField = 106
StatusCode_M_UnknownParameter = 107
StatusCode_M_UnknownField = 108
StatusCode_M_UnsupportedMessage = 109
StatusCode_M_UnsupportedVersion = 110
StatusCode_M_UnsupportedParameter = 111
StatusCode_P_ParameterError = 200
StatusCode_P_FieldError = 201
StatusCode_P_UnexpectedParameter = 202
StatusCode_P_MissingParameter = 203
StatusCode_P_DuplicateParameter = 204
StatusCode_P_OverflowParameter = 205
StatusCode_P_OverflowField = 206
StatusCode_P_UnknownParameter = 207
StatusCode_P_UnknownField = 208
StatusCode_P_UnsupportedParameter = 209
StatusCode_A_Invalid = 300
StatusCode_A_OutOfRange = 301
StatusCode_R_DeviceError = 401

#---------------------------------------------------------------------------
# C1G2DRValue
#
C1G2DRValue_DRV_8 = 0
C1G2DRValue_DRV_64_3 = 1

#---------------------------------------------------------------------------
# C1G2MValue
#
C1G2MValue_MV_FM0 = 0
C1G2MValue_MV_2 = 1
C1G2MValue_MV_4 = 2
C1G2MValue_MV_8 = 3

#---------------------------------------------------------------------------
# C1G2ForwardLinkModulation
#
C1G2ForwardLinkModulation_PR_ASK = 0
C1G2ForwardLinkModulation_SSB_ASK = 1
C1G2ForwardLinkModulation_DSB_ASK = 2

#---------------------------------------------------------------------------
# C1G2SpectralMaskIndicator
#
C1G2SpectralMaskIndicator_Unknown = 0
C1G2SpectralMaskIndicator_SI = 1
C1G2SpectralMaskIndicator_MI = 2
C1G2SpectralMaskIndicator_DI = 3

#---------------------------------------------------------------------------
# C1G2TruncateAction
#
C1G2TruncateAction_Unspecified = 0
C1G2TruncateAction_Do_Not_Truncate = 1
C1G2TruncateAction_Truncate = 2

#---------------------------------------------------------------------------
# C1G2StateAwareTarget
#
C1G2StateAwareTarget_SL = 0
C1G2StateAwareTarget_Inventoried_State_For_Session_S0 = 1
C1G2StateAwareTarget_Inventoried_State_For_Session_S1 = 2
C1G2StateAwareTarget_Inventoried_State_For_Session_S2 = 3
C1G2StateAwareTarget_Inventoried_State_For_Session_S3 = 4

#---------------------------------------------------------------------------
# C1G2StateAwareAction
#
C1G2StateAwareAction_AssertSLOrA_DeassertSLOrB = 0
C1G2StateAwareAction_AssertSLOrA_Noop = 1
C1G2StateAwareAction_Noop_DeassertSLOrB = 2
C1G2StateAwareAction_NegateSLOrABBA_Noop = 3
C1G2StateAwareAction_DeassertSLOrB_AssertSLOrA = 4
C1G2StateAwareAction_DeassertSLOrB_Noop = 5
C1G2StateAwareAction_Noop_AssertSLOrA = 6
C1G2StateAwareAction_Noop_NegateSLOrABBA = 7

#---------------------------------------------------------------------------
# C1G2StateUnawareAction
#
C1G2StateUnawareAction_Select_Unselect = 0
C1G2StateUnawareAction_Select_DoNothing = 1
C1G2StateUnawareAction_DoNothing_Unselect = 2
C1G2StateUnawareAction_Unselect_DoNothing = 3
C1G2StateUnawareAction_Unselect_Select = 4
C1G2StateUnawareAction_DoNothing_Select = 5

#---------------------------------------------------------------------------
# C1G2TagInventoryStateAwareI
#
C1G2TagInventoryStateAwareI_State_A = 0
C1G2TagInventoryStateAwareI_State_B = 1

#---------------------------------------------------------------------------
# C1G2TagInventoryStateAwareS
#
C1G2TagInventoryStateAwareS_SL = 0
C1G2TagInventoryStateAwareS_Not_SL = 1

#---------------------------------------------------------------------------
# C1G2LockPrivilege
#
C1G2LockPrivilege_Read_Write = 0
C1G2LockPrivilege_Perma_Lock = 1
C1G2LockPrivilege_Perma_Unlock = 2
C1G2LockPrivilege_Unlock = 3

#---------------------------------------------------------------------------
# C1G2LockDataField
#
C1G2LockDataField_Kill_Password = 0
C1G2LockDataField_Access_Password = 1
C1G2LockDataField_EPC_Memory = 2
C1G2LockDataField_TID_Memory = 3
C1G2LockDataField_User_Memory = 4

#---------------------------------------------------------------------------
# C1G2ReadResultType
#
C1G2ReadResultType_Success = 0
C1G2ReadResultType_Nonspecific_Tag_Error = 1
C1G2ReadResultType_No_Response_From_Tag = 2
C1G2ReadResultType_Nonspecific_Reader_Error = 3

#---------------------------------------------------------------------------
# C1G2WriteResultType
#
C1G2WriteResultType_Success = 0
C1G2WriteResultType_Tag_Memory_Overrun_Error = 1
C1G2WriteResultType_Tag_Memory_Locked_Error = 2
C1G2WriteResultType_Insufficient_Power = 3
C1G2WriteResultType_Nonspecific_Tag_Error = 4
C1G2WriteResultType_No_Response_From_Tag = 5
C1G2WriteResultType_Nonspecific_Reader_Error = 6

#---------------------------------------------------------------------------
# C1G2KillResultType
#
C1G2KillResultType_Success = 0
C1G2KillResultType_Zero_Kill_Password_Error = 1
C1G2KillResultType_Insufficient_Power = 2
C1G2KillResultType_Nonspecific_Tag_Error = 3
C1G2KillResultType_No_Response_From_Tag = 4
C1G2KillResultType_Nonspecific_Reader_Error = 5

#---------------------------------------------------------------------------
# C1G2LockResultType
#
C1G2LockResultType_Success = 0
C1G2LockResultType_Insufficient_Power = 1
C1G2LockResultType_Nonspecific_Tag_Error = 2
C1G2LockResultType_No_Response_From_Tag = 3
C1G2LockResultType_Nonspecific_Reader_Error = 4

#---------------------------------------------------------------------------
# C1G2BlockEraseResultType
#
C1G2BlockEraseResultType_Success = 0
C1G2BlockEraseResultType_Tag_Memory_Overrun_Error = 1
C1G2BlockEraseResultType_Tag_Memory_Locked_Error = 2
C1G2BlockEraseResultType_Insufficient_Power = 3
C1G2BlockEraseResultType_Nonspecific_Tag_Error = 4
C1G2BlockEraseResultType_No_Response_From_Tag = 5
C1G2BlockEraseResultType_Nonspecific_Reader_Error = 6

#---------------------------------------------------------------------------
# C1G2BlockWriteResultType
#
C1G2BlockWriteResultType_Success = 0
C1G2BlockWriteResultType_Tag_Memory_Overrun_Error = 1
C1G2BlockWriteResultType_Tag_Memory_Locked_Error = 2
C1G2BlockWriteResultType_Insufficient_Power = 3
C1G2BlockWriteResultType_Nonspecific_Tag_Error = 4
C1G2BlockWriteResultType_No_Response_From_Tag = 5
C1G2BlockWriteResultType_Nonspecific_Reader_Error = 6
