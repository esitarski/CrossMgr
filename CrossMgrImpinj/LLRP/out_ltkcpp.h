
/*
 * Generated file - DO NOT EDIT
 *
 * This is the header file for the LLRP Tool Kit (LTK)
 * C++ (aka cpp) implementation. It is generated into a .inc file
 * that is included by a platform specific .h header file.
 * That .h file takes care of prerequisites needed by this file.
 */


/*
 * Message classes - forward decls
 */

class CCUSTOM_MESSAGE;
class CGET_READER_CAPABILITIES;
class CGET_READER_CAPABILITIES_RESPONSE;
class CADD_ROSPEC;
class CADD_ROSPEC_RESPONSE;
class CDELETE_ROSPEC;
class CDELETE_ROSPEC_RESPONSE;
class CSTART_ROSPEC;
class CSTART_ROSPEC_RESPONSE;
class CSTOP_ROSPEC;
class CSTOP_ROSPEC_RESPONSE;
class CENABLE_ROSPEC;
class CENABLE_ROSPEC_RESPONSE;
class CDISABLE_ROSPEC;
class CDISABLE_ROSPEC_RESPONSE;
class CGET_ROSPECS;
class CGET_ROSPECS_RESPONSE;
class CADD_ACCESSSPEC;
class CADD_ACCESSSPEC_RESPONSE;
class CDELETE_ACCESSSPEC;
class CDELETE_ACCESSSPEC_RESPONSE;
class CENABLE_ACCESSSPEC;
class CENABLE_ACCESSSPEC_RESPONSE;
class CDISABLE_ACCESSSPEC;
class CDISABLE_ACCESSSPEC_RESPONSE;
class CGET_ACCESSSPECS;
class CGET_ACCESSSPECS_RESPONSE;
class CGET_READER_CONFIG;
class CGET_READER_CONFIG_RESPONSE;
class CSET_READER_CONFIG;
class CSET_READER_CONFIG_RESPONSE;
class CCLOSE_CONNECTION;
class CCLOSE_CONNECTION_RESPONSE;
class CGET_REPORT;
class CRO_ACCESS_REPORT;
class CKEEPALIVE;
class CKEEPALIVE_ACK;
class CREADER_EVENT_NOTIFICATION;
class CENABLE_EVENTS_AND_REPORTS;
class CERROR_MESSAGE;

/* Custom messages */


/*
 * Parameter classes - forward decls
 */

class CUTCTimestamp;
class CUptime;
class CCustom;
class CGeneralDeviceCapabilities;
class CReceiveSensitivityTableEntry;
class CPerAntennaReceiveSensitivityRange;
class CPerAntennaAirProtocol;
class CGPIOCapabilities;
class CLLRPCapabilities;
class CRegulatoryCapabilities;
class CUHFBandCapabilities;
class CTransmitPowerLevelTableEntry;
class CFrequencyInformation;
class CFrequencyHopTable;
class CFixedFrequencyTable;
class CROSpec;
class CROBoundarySpec;
class CROSpecStartTrigger;
class CPeriodicTriggerValue;
class CGPITriggerValue;
class CROSpecStopTrigger;
class CAISpec;
class CAISpecStopTrigger;
class CTagObservationTrigger;
class CInventoryParameterSpec;
class CRFSurveySpec;
class CRFSurveySpecStopTrigger;
class CAccessSpec;
class CAccessSpecStopTrigger;
class CAccessCommand;
class CLLRPConfigurationStateValue;
class CIdentification;
class CGPOWriteData;
class CKeepaliveSpec;
class CAntennaProperties;
class CAntennaConfiguration;
class CRFReceiver;
class CRFTransmitter;
class CGPIPortCurrentState;
class CEventsAndReports;
class CROReportSpec;
class CTagReportContentSelector;
class CAccessReportSpec;
class CTagReportData;
class CEPCData;
class CEPC_96;
class CROSpecID;
class CSpecIndex;
class CInventoryParameterSpecID;
class CAntennaID;
class CPeakRSSI;
class CChannelIndex;
class CFirstSeenTimestampUTC;
class CFirstSeenTimestampUptime;
class CLastSeenTimestampUTC;
class CLastSeenTimestampUptime;
class CTagSeenCount;
class CAccessSpecID;
class CRFSurveyReportData;
class CFrequencyRSSILevelEntry;
class CReaderEventNotificationSpec;
class CEventNotificationState;
class CReaderEventNotificationData;
class CHoppingEvent;
class CGPIEvent;
class CROSpecEvent;
class CReportBufferLevelWarningEvent;
class CReportBufferOverflowErrorEvent;
class CReaderExceptionEvent;
class COpSpecID;
class CRFSurveyEvent;
class CAISpecEvent;
class CAntennaEvent;
class CConnectionAttemptEvent;
class CConnectionCloseEvent;
class CLLRPStatus;
class CFieldError;
class CParameterError;
class CC1G2LLRPCapabilities;
class CC1G2UHFRFModeTable;
class CC1G2UHFRFModeTableEntry;
class CC1G2InventoryCommand;
class CC1G2Filter;
class CC1G2TagInventoryMask;
class CC1G2TagInventoryStateAwareFilterAction;
class CC1G2TagInventoryStateUnawareFilterAction;
class CC1G2RFControl;
class CC1G2SingulationControl;
class CC1G2TagInventoryStateAwareSingulationAction;
class CC1G2TagSpec;
class CC1G2TargetTag;
class CC1G2Read;
class CC1G2Write;
class CC1G2Kill;
class CC1G2Lock;
class CC1G2LockPayload;
class CC1G2BlockErase;
class CC1G2BlockWrite;
class CC1G2EPCMemorySelector;
class CC1G2_PC;
class CC1G2_CRC;
class CC1G2SingulationDetails;
class CC1G2ReadOpSpecResult;
class CC1G2WriteOpSpecResult;
class CC1G2KillOpSpecResult;
class CC1G2LockOpSpecResult;
class CC1G2BlockEraseOpSpecResult;
class CC1G2BlockWriteOpSpecResult;

/* Custom parameters */


/*
 * Vendor descriptor declarations.
 */


/*
 * Namespace descriptor declarations.
 */

extern const CNamespaceDescriptor
g_nsdescllrp;


/*
 * Enumeration definitions and declarations of
 * enumeration string tables.
 */


/**
 ** @brief  Global enumeration EAirProtocols for LLRP enumerated field AirProtocols
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=38&view=fit>LLRP Specification Section 7.1.4</a>
  </li>
  
</ul>  
             
      
        
    <p>This is the identifier of the air protocol. </p> 
 
       
  <HR>

    
    
    
  
 **/

enum EAirProtocols
{

    AirProtocols_Unspecified = 0, /**< Unspecified */ 
    AirProtocols_EPCGlobalClass1Gen2 = 1, /**< EPCGlobalClass1Gen2 */  
};

extern const SEnumTableEntry
g_estAirProtocols[];


/**
 ** @brief  Global enumeration EGetReaderCapabilitiesRequestedData for LLRP enumerated field GetReaderCapabilitiesRequestedData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=44&view=fit>LLRP Specification Section 9.1.1</a>
  </li>
  
</ul>  

    
    
    
    
    
    
  
 **/

enum EGetReaderCapabilitiesRequestedData
{

    GetReaderCapabilitiesRequestedData_All = 0, /**< All */ 
    GetReaderCapabilitiesRequestedData_General_Device_Capabilities = 1, /**< General_Device_Capabilities */ 
    GetReaderCapabilitiesRequestedData_LLRP_Capabilities = 2, /**< LLRP_Capabilities */ 
    GetReaderCapabilitiesRequestedData_Regulatory_Capabilities = 3, /**< Regulatory_Capabilities */ 
    GetReaderCapabilitiesRequestedData_LLRP_Air_Protocol_Capabilities = 4, /**< LLRP_Air_Protocol_Capabilities */  
};

extern const SEnumTableEntry
g_estGetReaderCapabilitiesRequestedData[];


/**
 ** @brief  Global enumeration ECommunicationsStandard for LLRP enumerated field CommunicationsStandard
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=49&view=fit>LLRP Specification Section 9.2.4</a>
  </li>
  
</ul>  

      
         
    <p>This field carries the enumerations of the communications standard.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
  
 **/

enum ECommunicationsStandard
{

    CommunicationsStandard_Unspecified = 0, /**< Unspecified */ 
    CommunicationsStandard_US_FCC_Part_15 = 1, /**< US_FCC_Part_15 */ 
    CommunicationsStandard_ETSI_302_208 = 2, /**< ETSI_302_208 */ 
    CommunicationsStandard_ETSI_300_220 = 3, /**< ETSI_300_220 */ 
    CommunicationsStandard_Australia_LIPD_1W = 4, /**< Australia_LIPD_1W */ 
    CommunicationsStandard_Australia_LIPD_4W = 5, /**< Australia_LIPD_4W */ 
    CommunicationsStandard_Japan_ARIB_STD_T89 = 6, /**< Japan_ARIB_STD_T89 */ 
    CommunicationsStandard_Hong_Kong_OFTA_1049 = 7, /**< Hong_Kong_OFTA_1049 */ 
    CommunicationsStandard_Taiwan_DGT_LP0002 = 8, /**< Taiwan_DGT_LP0002 */ 
    CommunicationsStandard_Korea_MIC_Article_5_2 = 9, /**< Korea_MIC_Article_5_2 */  
};

extern const SEnumTableEntry
g_estCommunicationsStandard[];


/**
 ** @brief  Global enumeration EROSpecState for LLRP enumerated field ROSpecState
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=55&view=fit>LLRP Specification Section 10.2.1</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EROSpecState
{

    ROSpecState_Disabled = 0, /**< Disabled */ 
    ROSpecState_Inactive = 1, /**< Inactive */ 
    ROSpecState_Active = 2, /**< Active */  
};

extern const SEnumTableEntry
g_estROSpecState[];


/**
 ** @brief  Global enumeration EROSpecStartTriggerType for LLRP enumerated field ROSpecStartTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=56&view=fit>LLRP Specification Section 10.2.1.1.1</a>
  </li>
  
</ul>  

      
        
    <p>Description</p> 
 
        
    <ul>
          
    <li>
    <p>0:    Null.  No start trigger. The only way to start this ROSpec is with a START_ROSPEC from the Client.</p> 
 </li>
 
           
    <li>
    <p>1:    Immediate</p> 
 </li>
 
           
    <li>
    <p>2:    Periodic</p> 
 </li>
 
           
    <li>
    <p>3:    GPI</p> 
 </li>
 
          </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

enum EROSpecStartTriggerType
{

    ROSpecStartTriggerType_Null = 0, /**< Null */ 
    ROSpecStartTriggerType_Immediate = 1, /**< Immediate */ 
    ROSpecStartTriggerType_Periodic = 2, /**< Periodic */ 
    ROSpecStartTriggerType_GPI = 3, /**< GPI */  
};

extern const SEnumTableEntry
g_estROSpecStartTriggerType[];


/**
 ** @brief  Global enumeration EROSpecStopTriggerType for LLRP enumerated field ROSpecStopTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=57&view=fit>LLRP Specification Section 10.2.1.1.2</a>
  </li>
  
</ul>  

      
       
    <p>Description</p> 
 
         
    <ul>
           
    <li>
    <p>0:    Null - Stop when all AISpecs are done, or when preempted, or with a STOP_ROSPEC from the Client.</p> 
 </li>
 
           
    <li>
    <p>1:    Duration</p> 
 </li>
 
           
    <li>
    <p>2:    GPI with a timeout value</p> 
 </li>
 
         </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

enum EROSpecStopTriggerType
{

    ROSpecStopTriggerType_Null = 0, /**< Null */ 
    ROSpecStopTriggerType_Duration = 1, /**< Duration */ 
    ROSpecStopTriggerType_GPI_With_Timeout = 2, /**< GPI_With_Timeout */  
};

extern const SEnumTableEntry
g_estROSpecStopTriggerType[];


/**
 ** @brief  Global enumeration EAISpecStopTriggerType for LLRP enumerated field AISpecStopTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=58&view=fit>LLRP Specification Section 10.2.2.1</a>
  </li>
  
</ul>  

      
        
    <p>Description:</p> 
 
          
    <ul>
            
    <li>
    <p>0:    Null - Stop when ROSpec is done.</p> 
 </li>
 
           
    <li>
    <p>1:    Duration</p> 
 </li>
 
           
    <li>
    <p>2:    GPI with a timeout value</p> 
 </li>
 
           
    <li>
    <p>3:    Tag observation</p> 
 </li>
 
         </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

enum EAISpecStopTriggerType
{

    AISpecStopTriggerType_Null = 0, /**< Null */ 
    AISpecStopTriggerType_Duration = 1, /**< Duration */ 
    AISpecStopTriggerType_GPI_With_Timeout = 2, /**< GPI_With_Timeout */ 
    AISpecStopTriggerType_Tag_Observation = 3, /**< Tag_Observation */  
};

extern const SEnumTableEntry
g_estAISpecStopTriggerType[];


/**
 ** @brief  Global enumeration ETagObservationTriggerType for LLRP enumerated field TagObservationTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=58&view=fit>LLRP Specification Section 10.2.2.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Description:</p> 
 
         
    <ul>
            
    <li>
    <p>0:    Upon seeing N tag observations, or timeout</p> 
 </li>
 
           
    <li>
    <p>1:    Upon seeing no more new tag observations for t ms, or timeout</p> 
 </li>
 
           
    <li>
    <p>2:    N attempts to see all tags in the FOV, or timeout</p> 
 </li>
 
         </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

enum ETagObservationTriggerType
{

    TagObservationTriggerType_Upon_Seeing_N_Tags_Or_Timeout = 0, /**< Upon_Seeing_N_Tags_Or_Timeout */ 
    TagObservationTriggerType_Upon_Seeing_No_More_New_Tags_For_Tms_Or_Timeout = 1, /**< Upon_Seeing_No_More_New_Tags_For_Tms_Or_Timeout */ 
    TagObservationTriggerType_N_Attempts_To_See_All_Tags_In_FOV_Or_Timeout = 2, /**< N_Attempts_To_See_All_Tags_In_FOV_Or_Timeout */  
};

extern const SEnumTableEntry
g_estTagObservationTriggerType[];


/**
 ** @brief  Global enumeration ERFSurveySpecStopTriggerType for LLRP enumerated field RFSurveySpecStopTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=60&view=fit>LLRP Specification Section 10.2.3.1</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum ERFSurveySpecStopTriggerType
{

    RFSurveySpecStopTriggerType_Null = 0, /**< Null */ 
    RFSurveySpecStopTriggerType_Duration = 1, /**< Duration */ 
    RFSurveySpecStopTriggerType_N_Iterations_Through_Frequency_Range = 2, /**< N_Iterations_Through_Frequency_Range */  
};

extern const SEnumTableEntry
g_estRFSurveySpecStopTriggerType[];


/**
 ** @brief  Global enumeration EAccessSpecState for LLRP enumerated field AccessSpecState
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=64&view=fit>LLRP Specification Section 11.2.1</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EAccessSpecState
{

    AccessSpecState_Disabled = 0, /**< Disabled */ 
    AccessSpecState_Active = 1, /**< Active */  
};

extern const SEnumTableEntry
g_estAccessSpecState[];


/**
 ** @brief  Global enumeration EAccessSpecStopTriggerType for LLRP enumerated field AccessSpecStopTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=65&view=fit>LLRP Specification Section 11.2.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Description:</p> 
 
            
    <ul>
              
    <li>
    <p>0:    Null - No stop trigger defined.</p> 
 </li>
 
           
    <li>
    <p>1:     Operation count</p> 
 </li>
 
         </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

enum EAccessSpecStopTriggerType
{

    AccessSpecStopTriggerType_Null = 0, /**< Null */ 
    AccessSpecStopTriggerType_Operation_Count = 1, /**< Operation_Count */  
};

extern const SEnumTableEntry
g_estAccessSpecStopTriggerType[];


/**
 ** @brief  Global enumeration EGetReaderConfigRequestedData for LLRP enumerated field GetReaderConfigRequestedData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=67&view=fit>LLRP Specification Section 12.1.1</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

enum EGetReaderConfigRequestedData
{

    GetReaderConfigRequestedData_All = 0, /**< All */ 
    GetReaderConfigRequestedData_Identification = 1, /**< Identification */ 
    GetReaderConfigRequestedData_AntennaProperties = 2, /**< AntennaProperties */ 
    GetReaderConfigRequestedData_AntennaConfiguration = 3, /**< AntennaConfiguration */ 
    GetReaderConfigRequestedData_ROReportSpec = 4, /**< ROReportSpec */ 
    GetReaderConfigRequestedData_ReaderEventNotificationSpec = 5, /**< ReaderEventNotificationSpec */ 
    GetReaderConfigRequestedData_AccessReportSpec = 6, /**< AccessReportSpec */ 
    GetReaderConfigRequestedData_LLRPConfigurationStateValue = 7, /**< LLRPConfigurationStateValue */ 
    GetReaderConfigRequestedData_KeepaliveSpec = 8, /**< KeepaliveSpec */ 
    GetReaderConfigRequestedData_GPIPortCurrentState = 9, /**< GPIPortCurrentState */ 
    GetReaderConfigRequestedData_GPOWriteData = 10, /**< GPOWriteData */ 
    GetReaderConfigRequestedData_EventsAndReports = 11, /**< EventsAndReports */  
};

extern const SEnumTableEntry
g_estGetReaderConfigRequestedData[];


/**
 ** @brief  Global enumeration EIdentificationType for LLRP enumerated field IdentificationType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=72&view=fit>LLRP Specification Section 12.2.2</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EIdentificationType
{

    IdentificationType_MAC_Address = 0, /**< MAC_Address */ 
    IdentificationType_EPC = 1, /**< EPC */  
};

extern const SEnumTableEntry
g_estIdentificationType[];


/**
 ** @brief  Global enumeration EKeepaliveTriggerType for LLRP enumerated field KeepaliveTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=73&view=fit>LLRP Specification Section 12.2.4</a>
  </li>
  
</ul>  

      
          
    <p>Description:</p> 
 
        
    <ul>
          
    <li>
    <p>0:    Null - No keepalives 
   <b>SHALL</b>
  be sent by the Reader</p> 
 </li>
 
          
    <li>
    <p>1:    Periodic</p> 
 </li>
 
        </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

enum EKeepaliveTriggerType
{

    KeepaliveTriggerType_Null = 0, /**< Null */ 
    KeepaliveTriggerType_Periodic = 1, /**< Periodic */  
};

extern const SEnumTableEntry
g_estKeepaliveTriggerType[];


/**
 ** @brief  Global enumeration EGPIPortState for LLRP enumerated field GPIPortState
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=75&view=fit>LLRP Specification Section 12.2.6.3</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EGPIPortState
{

    GPIPortState_Low = 0, /**< Low */ 
    GPIPortState_High = 1, /**< High */ 
    GPIPortState_Unknown = 2, /**< Unknown */  
};

extern const SEnumTableEntry
g_estGPIPortState[];


/**
 ** @brief  Global enumeration EROReportTriggerType for LLRP enumerated field ROReportTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=78&view=fit>LLRP Specification Section 13.2.1</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EROReportTriggerType
{

    ROReportTriggerType_None = 0, /**< None */ 
    ROReportTriggerType_Upon_N_Tags_Or_End_Of_AISpec = 1, /**< Upon_N_Tags_Or_End_Of_AISpec */ 
    ROReportTriggerType_Upon_N_Tags_Or_End_Of_ROSpec = 2, /**< Upon_N_Tags_Or_End_Of_ROSpec */  
};

extern const SEnumTableEntry
g_estROReportTriggerType[];


/**
 ** @brief  Global enumeration EAccessReportTriggerType for LLRP enumerated field AccessReportTriggerType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=80&view=fit>LLRP Specification Section 13.2.2</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EAccessReportTriggerType
{

    AccessReportTriggerType_Whenever_ROReport_Is_Generated = 0, /**< Whenever_ROReport_Is_Generated */ 
    AccessReportTriggerType_End_Of_AccessSpec = 1, /**< End_Of_AccessSpec */  
};

extern const SEnumTableEntry
g_estAccessReportTriggerType[];


/**
 ** @brief  Global enumeration ENotificationEventType for LLRP enumerated field NotificationEventType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=86&view=fit>LLRP Specification Section 13.2.5.1</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
    
    
    
  
 **/

enum ENotificationEventType
{

    NotificationEventType_Upon_Hopping_To_Next_Channel = 0, /**< Upon_Hopping_To_Next_Channel */ 
    NotificationEventType_GPI_Event = 1, /**< GPI_Event */ 
    NotificationEventType_ROSpec_Event = 2, /**< ROSpec_Event */ 
    NotificationEventType_Report_Buffer_Fill_Warning = 3, /**< Report_Buffer_Fill_Warning */ 
    NotificationEventType_Reader_Exception_Event = 4, /**< Reader_Exception_Event */ 
    NotificationEventType_RFSurvey_Event = 5, /**< RFSurvey_Event */ 
    NotificationEventType_AISpec_Event = 6, /**< AISpec_Event */ 
    NotificationEventType_AISpec_Event_With_Details = 7, /**< AISpec_Event_With_Details */ 
    NotificationEventType_Antenna_Event = 8, /**< Antenna_Event */  
};

extern const SEnumTableEntry
g_estNotificationEventType[];


/**
 ** @brief  Global enumeration EROSpecEventType for LLRP enumerated field ROSpecEventType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=89&view=fit>LLRP Specification Section 13.2.6.4</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EROSpecEventType
{

    ROSpecEventType_Start_Of_ROSpec = 0, /**< Start_Of_ROSpec */ 
    ROSpecEventType_End_Of_ROSpec = 1, /**< End_Of_ROSpec */ 
    ROSpecEventType_Preemption_Of_ROSpec = 2, /**< Preemption_Of_ROSpec */  
};

extern const SEnumTableEntry
g_estROSpecEventType[];


/**
 ** @brief  Global enumeration ERFSurveyEventType for LLRP enumerated field RFSurveyEventType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=90&view=fit>LLRP Specification Section 13.2.6.8</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum ERFSurveyEventType
{

    RFSurveyEventType_Start_Of_RFSurvey = 0, /**< Start_Of_RFSurvey */ 
    RFSurveyEventType_End_Of_RFSurvey = 1, /**< End_Of_RFSurvey */  
};

extern const SEnumTableEntry
g_estRFSurveyEventType[];


/**
 ** @brief  Global enumeration EAISpecEventType for LLRP enumerated field AISpecEventType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=91&view=fit>LLRP Specification Section 13.2.6.9</a>
  </li>
  
</ul>  

    
    
  
 **/

enum EAISpecEventType
{

    AISpecEventType_End_Of_AISpec = 0, /**< End_Of_AISpec */  
};

extern const SEnumTableEntry
g_estAISpecEventType[];


/**
 ** @brief  Global enumeration EAntennaEventType for LLRP enumerated field AntennaEventType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=91&view=fit>LLRP Specification Section 13.2.6.10</a>
  </li>
  
</ul>  


    
    
    
  
 **/

enum EAntennaEventType
{

    AntennaEventType_Antenna_Disconnected = 0, /**< Antenna_Disconnected */ 
    AntennaEventType_Antenna_Connected = 1, /**< Antenna_Connected */  
};

extern const SEnumTableEntry
g_estAntennaEventType[];


/**
 ** @brief  Global enumeration EConnectionAttemptStatusType for LLRP enumerated field ConnectionAttemptStatusType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=92&view=fit>LLRP Specification Section 13.2.6.11</a>
  </li>
  
</ul>  

      
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

enum EConnectionAttemptStatusType
{

    ConnectionAttemptStatusType_Success = 0, /**< Success */ 
    ConnectionAttemptStatusType_Failed_A_Reader_Initiated_Connection_Already_Exists = 1, /**< Failed_A_Reader_Initiated_Connection_Already_Exists */ 
    ConnectionAttemptStatusType_Failed_A_Client_Initiated_Connection_Already_Exists = 2, /**< Failed_A_Client_Initiated_Connection_Already_Exists */ 
    ConnectionAttemptStatusType_Failed_Reason_Other_Than_A_Connection_Already_Exists = 3, /**< Failed_Reason_Other_Than_A_Connection_Already_Exists */ 
    ConnectionAttemptStatusType_Another_Connection_Attempted = 4, /**< Another_Connection_Attempted */  
};

extern const SEnumTableEntry
g_estConnectionAttemptStatusType[];


/**
 ** @brief  Global enumeration EStatusCode for LLRP enumerated field StatusCode
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=93&view=fit>LLRP Specification Section 14.2.1</a>
  </li>
  
</ul>  

      
          
    <p>Status can be a success or one of the error conditions. This section lists a set of generic error conditions that, in combination with the identifier of the culprit field, conveys the error condition. The codes are broken into four scopes: message, parameter,  field and device. The device code indicates that the error is in the Reader device rather than the message, parameter or field.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

enum EStatusCode
{

    StatusCode_M_Success = 0, /**< M_Success */ 
    StatusCode_M_ParameterError = 100, /**< M_ParameterError */ 
    StatusCode_M_FieldError = 101, /**< M_FieldError */ 
    StatusCode_M_UnexpectedParameter = 102, /**< M_UnexpectedParameter */ 
    StatusCode_M_MissingParameter = 103, /**< M_MissingParameter */ 
    StatusCode_M_DuplicateParameter = 104, /**< M_DuplicateParameter */ 
    StatusCode_M_OverflowParameter = 105, /**< M_OverflowParameter */ 
    StatusCode_M_OverflowField = 106, /**< M_OverflowField */ 
    StatusCode_M_UnknownParameter = 107, /**< M_UnknownParameter */ 
    StatusCode_M_UnknownField = 108, /**< M_UnknownField */ 
    StatusCode_M_UnsupportedMessage = 109, /**< M_UnsupportedMessage */ 
    StatusCode_M_UnsupportedVersion = 110, /**< M_UnsupportedVersion */ 
    StatusCode_M_UnsupportedParameter = 111, /**< M_UnsupportedParameter */ 
    StatusCode_P_ParameterError = 200, /**< P_ParameterError */ 
    StatusCode_P_FieldError = 201, /**< P_FieldError */ 
    StatusCode_P_UnexpectedParameter = 202, /**< P_UnexpectedParameter */ 
    StatusCode_P_MissingParameter = 203, /**< P_MissingParameter */ 
    StatusCode_P_DuplicateParameter = 204, /**< P_DuplicateParameter */ 
    StatusCode_P_OverflowParameter = 205, /**< P_OverflowParameter */ 
    StatusCode_P_OverflowField = 206, /**< P_OverflowField */ 
    StatusCode_P_UnknownParameter = 207, /**< P_UnknownParameter */ 
    StatusCode_P_UnknownField = 208, /**< P_UnknownField */ 
    StatusCode_P_UnsupportedParameter = 209, /**< P_UnsupportedParameter */ 
    StatusCode_A_Invalid = 300, /**< A_Invalid */ 
    StatusCode_A_OutOfRange = 301, /**< A_OutOfRange */ 
    StatusCode_R_DeviceError = 401, /**< R_DeviceError */  
};

extern const SEnumTableEntry
g_estStatusCode[];


/**
 ** @brief  Global enumeration EC1G2DRValue for LLRP enumerated field C1G2DRValue
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=99&view=fit>LLRP Specification Section 15.2.1.1.2.1</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EC1G2DRValue
{

    C1G2DRValue_DRV_8 = 0, /**< DRV_8 */ 
    C1G2DRValue_DRV_64_3 = 1, /**< DRV_64_3 */  
};

extern const SEnumTableEntry
g_estC1G2DRValue[];


/**
 ** @brief  Global enumeration EC1G2MValue for LLRP enumerated field C1G2MValue
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=99&view=fit>LLRP Specification Section 15.2.1.1.2.1</a>
  </li>
  
</ul>  

    
    
    
    
    
  
 **/

enum EC1G2MValue
{

    C1G2MValue_MV_FM0 = 0, /**< MV_FM0 */ 
    C1G2MValue_MV_2 = 1, /**< MV_2 */ 
    C1G2MValue_MV_4 = 2, /**< MV_4 */ 
    C1G2MValue_MV_8 = 3, /**< MV_8 */  
};

extern const SEnumTableEntry
g_estC1G2MValue[];


/**
 ** @brief  Global enumeration EC1G2ForwardLinkModulation for LLRP enumerated field C1G2ForwardLinkModulation
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=99&view=fit>LLRP Specification Section 15.2.1.1.2.1</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EC1G2ForwardLinkModulation
{

    C1G2ForwardLinkModulation_PR_ASK = 0, /**< PR_ASK */ 
    C1G2ForwardLinkModulation_SSB_ASK = 1, /**< SSB_ASK */ 
    C1G2ForwardLinkModulation_DSB_ASK = 2, /**< DSB_ASK */  
};

extern const SEnumTableEntry
g_estC1G2ForwardLinkModulation[];


/**
 ** @brief  Global enumeration EC1G2SpectralMaskIndicator for LLRP enumerated field C1G2SpectralMaskIndicator
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=100&view=fit>LLRP Specification Section 15.2.1.1.2.1</a>
  </li>
  
</ul>  

      
        
    <p>Description</p> 
 
        
    <ul>
          
    <li>
    <p>0:          Unknown</p> 
 </li>
 
          
    <li>
    <p>1:          SI -Meets [C1G2] Single-Interrogator Mode Mask</p> 
 </li>
 
          
    <li>
    <p>2:          MI - Meets [C1G2] Multi-Interrogator Mode Mask</p> 
 </li>
 
          
    <li>
    <p>3:          DI - Meets [C1G2] Dense-Interrogator Mode Mask</p> 
 </li>
 
        </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

enum EC1G2SpectralMaskIndicator
{

    C1G2SpectralMaskIndicator_Unknown = 0, /**< Unknown */ 
    C1G2SpectralMaskIndicator_SI = 1, /**< SI */ 
    C1G2SpectralMaskIndicator_MI = 2, /**< MI */ 
    C1G2SpectralMaskIndicator_DI = 3, /**< DI */  
};

extern const SEnumTableEntry
g_estC1G2SpectralMaskIndicator[];


/**
 ** @brief  Global enumeration EC1G2TruncateAction for LLRP enumerated field C1G2TruncateAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=102&view=fit>LLRP Specification Section 15.2.1.2.1.1</a>
  </li>
  
</ul>  

    
    
    
    
  
 **/

enum EC1G2TruncateAction
{

    C1G2TruncateAction_Unspecified = 0, /**< Unspecified */ 
    C1G2TruncateAction_Do_Not_Truncate = 1, /**< Do_Not_Truncate */ 
    C1G2TruncateAction_Truncate = 2, /**< Truncate */  
};

extern const SEnumTableEntry
g_estC1G2TruncateAction[];


/**
 ** @brief  Global enumeration EC1G2StateAwareTarget for LLRP enumerated field C1G2StateAwareTarget
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=103&view=fit>LLRP Specification Section 15.2.1.2.1.1.2</a>
  </li>
  
</ul>  

    
    
    
    
    
    
  
 **/

enum EC1G2StateAwareTarget
{

    C1G2StateAwareTarget_SL = 0, /**< SL */ 
    C1G2StateAwareTarget_Inventoried_State_For_Session_S0 = 1, /**< Inventoried_State_For_Session_S0 */ 
    C1G2StateAwareTarget_Inventoried_State_For_Session_S1 = 2, /**< Inventoried_State_For_Session_S1 */ 
    C1G2StateAwareTarget_Inventoried_State_For_Session_S2 = 3, /**< Inventoried_State_For_Session_S2 */ 
    C1G2StateAwareTarget_Inventoried_State_For_Session_S3 = 4, /**< Inventoried_State_For_Session_S3 */  
};

extern const SEnumTableEntry
g_estC1G2StateAwareTarget[];


/**
 ** @brief  Global enumeration EC1G2StateAwareAction for LLRP enumerated field C1G2StateAwareAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=103&view=fit>LLRP Specification Section 15.2.1.2.1.1.2</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
    
    
  
 **/

enum EC1G2StateAwareAction
{

    C1G2StateAwareAction_AssertSLOrA_DeassertSLOrB = 0, /**< AssertSLOrA_DeassertSLOrB */ 
    C1G2StateAwareAction_AssertSLOrA_Noop = 1, /**< AssertSLOrA_Noop */ 
    C1G2StateAwareAction_Noop_DeassertSLOrB = 2, /**< Noop_DeassertSLOrB */ 
    C1G2StateAwareAction_NegateSLOrABBA_Noop = 3, /**< NegateSLOrABBA_Noop */ 
    C1G2StateAwareAction_DeassertSLOrB_AssertSLOrA = 4, /**< DeassertSLOrB_AssertSLOrA */ 
    C1G2StateAwareAction_DeassertSLOrB_Noop = 5, /**< DeassertSLOrB_Noop */ 
    C1G2StateAwareAction_Noop_AssertSLOrA = 6, /**< Noop_AssertSLOrA */ 
    C1G2StateAwareAction_Noop_NegateSLOrABBA = 7, /**< Noop_NegateSLOrABBA */  
};

extern const SEnumTableEntry
g_estC1G2StateAwareAction[];


/**
 ** @brief  Global enumeration EC1G2StateUnawareAction for LLRP enumerated field C1G2StateUnawareAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=104&view=fit>LLRP Specification Section 15.2.1.2.1.1.3</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
  
 **/

enum EC1G2StateUnawareAction
{

    C1G2StateUnawareAction_Select_Unselect = 0, /**< Select_Unselect */ 
    C1G2StateUnawareAction_Select_DoNothing = 1, /**< Select_DoNothing */ 
    C1G2StateUnawareAction_DoNothing_Unselect = 2, /**< DoNothing_Unselect */ 
    C1G2StateUnawareAction_Unselect_DoNothing = 3, /**< Unselect_DoNothing */ 
    C1G2StateUnawareAction_Unselect_Select = 4, /**< Unselect_Select */ 
    C1G2StateUnawareAction_DoNothing_Select = 5, /**< DoNothing_Select */  
};

extern const SEnumTableEntry
g_estC1G2StateUnawareAction[];


/**
 ** @brief  Global enumeration EC1G2TagInventoryStateAwareI for LLRP enumerated field C1G2TagInventoryStateAwareI
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=105&view=fit>LLRP Specification Section 15.2.1.2.1.3.1</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EC1G2TagInventoryStateAwareI
{

    C1G2TagInventoryStateAwareI_State_A = 0, /**< State_A */ 
    C1G2TagInventoryStateAwareI_State_B = 1, /**< State_B */  
};

extern const SEnumTableEntry
g_estC1G2TagInventoryStateAwareI[];


/**
 ** @brief  Global enumeration EC1G2TagInventoryStateAwareS for LLRP enumerated field C1G2TagInventoryStateAwareS
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=106&view=fit>LLRP Specification Section 15.2.1.2.1.3.1</a>
  </li>
  
</ul>  

    
    
    
  
 **/

enum EC1G2TagInventoryStateAwareS
{

    C1G2TagInventoryStateAwareS_SL = 0, /**< SL */ 
    C1G2TagInventoryStateAwareS_Not_SL = 1, /**< Not_SL */  
};

extern const SEnumTableEntry
g_estC1G2TagInventoryStateAwareS[];


/**
 ** @brief  Global enumeration EC1G2LockPrivilege for LLRP enumerated field C1G2LockPrivilege
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=109&view=fit>LLRP Specification Section 15.2.1.3.2.4.1</a>
  </li>
  
</ul>  

      
             
    <p>Read_Write means lock for either reading or writing (depends on memory bank).</p> 
 
       
  <HR>

    
    
    
    
    
  
 **/

enum EC1G2LockPrivilege
{

    C1G2LockPrivilege_Read_Write = 0, /**< Read_Write */ 
    C1G2LockPrivilege_Perma_Lock = 1, /**< Perma_Lock */ 
    C1G2LockPrivilege_Perma_Unlock = 2, /**< Perma_Unlock */ 
    C1G2LockPrivilege_Unlock = 3, /**< Unlock */  
};

extern const SEnumTableEntry
g_estC1G2LockPrivilege[];


/**
 ** @brief  Global enumeration EC1G2LockDataField for LLRP enumerated field C1G2LockDataField
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=109&view=fit>LLRP Specification Section 15.2.1.3.2.4.1</a>
  </li>
  
</ul>  

    
    
    
    
    
    
  
 **/

enum EC1G2LockDataField
{

    C1G2LockDataField_Kill_Password = 0, /**< Kill_Password */ 
    C1G2LockDataField_Access_Password = 1, /**< Access_Password */ 
    C1G2LockDataField_EPC_Memory = 2, /**< EPC_Memory */ 
    C1G2LockDataField_TID_Memory = 3, /**< TID_Memory */ 
    C1G2LockDataField_User_Memory = 4, /**< User_Memory */  
};

extern const SEnumTableEntry
g_estC1G2LockDataField[];


/**
 ** @brief  Global enumeration EC1G2ReadResultType for LLRP enumerated field C1G2ReadResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=112&view=fit>LLRP Specification Section 15.2.1.5.5.1</a>
  </li>
  
</ul>  

    
    
    
    
    
  
 **/

enum EC1G2ReadResultType
{

    C1G2ReadResultType_Success = 0, /**< Success */ 
    C1G2ReadResultType_Nonspecific_Tag_Error = 1, /**< Nonspecific_Tag_Error */ 
    C1G2ReadResultType_No_Response_From_Tag = 2, /**< No_Response_From_Tag */ 
    C1G2ReadResultType_Nonspecific_Reader_Error = 3, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2ReadResultType[];


/**
 ** @brief  Global enumeration EC1G2WriteResultType for LLRP enumerated field C1G2WriteResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=112&view=fit>LLRP Specification Section 15.2.1.5.5.2</a>
  </li>
  
</ul>  

      
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
  
 **/

enum EC1G2WriteResultType
{

    C1G2WriteResultType_Success = 0, /**< Success */ 
    C1G2WriteResultType_Tag_Memory_Overrun_Error = 1, /**< Tag_Memory_Overrun_Error */ 
    C1G2WriteResultType_Tag_Memory_Locked_Error = 2, /**< Tag_Memory_Locked_Error */ 
    C1G2WriteResultType_Insufficient_Power = 3, /**< Insufficient_Power */ 
    C1G2WriteResultType_Nonspecific_Tag_Error = 4, /**< Nonspecific_Tag_Error */ 
    C1G2WriteResultType_No_Response_From_Tag = 5, /**< No_Response_From_Tag */ 
    C1G2WriteResultType_Nonspecific_Reader_Error = 6, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2WriteResultType[];


/**
 ** @brief  Global enumeration EC1G2KillResultType for LLRP enumerated field C1G2KillResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=112&view=fit>LLRP Specification Section 15.2.1.5.5.3</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
  
 **/

enum EC1G2KillResultType
{

    C1G2KillResultType_Success = 0, /**< Success */ 
    C1G2KillResultType_Zero_Kill_Password_Error = 1, /**< Zero_Kill_Password_Error */ 
    C1G2KillResultType_Insufficient_Power = 2, /**< Insufficient_Power */ 
    C1G2KillResultType_Nonspecific_Tag_Error = 3, /**< Nonspecific_Tag_Error */ 
    C1G2KillResultType_No_Response_From_Tag = 4, /**< No_Response_From_Tag */ 
    C1G2KillResultType_Nonspecific_Reader_Error = 5, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2KillResultType[];


/**
 ** @brief  Global enumeration EC1G2LockResultType for LLRP enumerated field C1G2LockResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.4</a>
  </li>
  
</ul>  

    
    
    
    
    
    
  
 **/

enum EC1G2LockResultType
{

    C1G2LockResultType_Success = 0, /**< Success */ 
    C1G2LockResultType_Insufficient_Power = 1, /**< Insufficient_Power */ 
    C1G2LockResultType_Nonspecific_Tag_Error = 2, /**< Nonspecific_Tag_Error */ 
    C1G2LockResultType_No_Response_From_Tag = 3, /**< No_Response_From_Tag */ 
    C1G2LockResultType_Nonspecific_Reader_Error = 4, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2LockResultType[];


/**
 ** @brief  Global enumeration EC1G2BlockEraseResultType for LLRP enumerated field C1G2BlockEraseResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.5</a>
  </li>
  
</ul>  

    
    
    
    
    
    
    
    
  
 **/

enum EC1G2BlockEraseResultType
{

    C1G2BlockEraseResultType_Success = 0, /**< Success */ 
    C1G2BlockEraseResultType_Tag_Memory_Overrun_Error = 1, /**< Tag_Memory_Overrun_Error */ 
    C1G2BlockEraseResultType_Tag_Memory_Locked_Error = 2, /**< Tag_Memory_Locked_Error */ 
    C1G2BlockEraseResultType_Insufficient_Power = 3, /**< Insufficient_Power */ 
    C1G2BlockEraseResultType_Nonspecific_Tag_Error = 4, /**< Nonspecific_Tag_Error */ 
    C1G2BlockEraseResultType_No_Response_From_Tag = 5, /**< No_Response_From_Tag */ 
    C1G2BlockEraseResultType_Nonspecific_Reader_Error = 6, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2BlockEraseResultType[];


/**
 ** @brief  Global enumeration EC1G2BlockWriteResultType for LLRP enumerated field C1G2BlockWriteResultType
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.6</a>
  </li>
  
</ul>  

      
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
  
 **/

enum EC1G2BlockWriteResultType
{

    C1G2BlockWriteResultType_Success = 0, /**< Success */ 
    C1G2BlockWriteResultType_Tag_Memory_Overrun_Error = 1, /**< Tag_Memory_Overrun_Error */ 
    C1G2BlockWriteResultType_Tag_Memory_Locked_Error = 2, /**< Tag_Memory_Locked_Error */ 
    C1G2BlockWriteResultType_Insufficient_Power = 3, /**< Insufficient_Power */ 
    C1G2BlockWriteResultType_Nonspecific_Tag_Error = 4, /**< Nonspecific_Tag_Error */ 
    C1G2BlockWriteResultType_No_Response_From_Tag = 5, /**< No_Response_From_Tag */ 
    C1G2BlockWriteResultType_Nonspecific_Reader_Error = 6, /**< Nonspecific_Reader_Error */  
};

extern const SEnumTableEntry
g_estC1G2BlockWriteResultType[];


/** 
 * \defgroup CoreMessage  Core Message Classes
 * Classes to manipulate the messages defined by the Core LLRP protocol
 */
/*@{*/ 

/**
 ** @brief  Class Definition CCUSTOM_MESSAGE for LLRP message CUSTOM_MESSAGE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=42&view=fit>LLRP Specification Section 8.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=129&view=fit>LLRP Specification Section 16.1.42</a>
  </li>
  
</ul>  
                
      
           
    <p>This message carries a vendor defined format from Reader to Client or Client to Reader. </p> 
 
           
    <p>No requirements are made as to the content or parameters contained within the Data portion of these messages. Clients 
   <b>MAY</b>
  ignore CUSTOM_MESSAGEs. Readers 
   <b>SHALL</b>
  accept CUSTOM_MESSAGE and return an ERROR_MESSAGE if CUSTOM_MESSAGE is unsupported by the Reader or the CUSTOM_MESSAGE contains fields and/or parameters that are unsupported by the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CCUSTOM_MESSAGE : public CMessage
{
  public:
    CCUSTOM_MESSAGE (void);
    ~CCUSTOM_MESSAGE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_VendorIdentifier;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdVendorIdentifier;
//@}

    /** @brief Get accessor functions for the LLRP VendorIdentifier field */
    inline llrp_u32_t
    getVendorIdentifier (void)
    {
        return m_VendorIdentifier;
    }

    /** @brief Set accessor functions for the LLRP VendorIdentifier field */
    inline void
    setVendorIdentifier (
      llrp_u32_t value)
    {
        m_VendorIdentifier = value;
    }


  
  
  
  protected:
    llrp_u8_t m_MessageSubtype;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMessageSubtype;
//@}

    /** @brief Get accessor functions for the LLRP MessageSubtype field */
    inline llrp_u8_t
    getMessageSubtype (void)
    {
        return m_MessageSubtype;
    }

    /** @brief Set accessor functions for the LLRP MessageSubtype field */
    inline void
    setMessageSubtype (
      llrp_u8_t value)
    {
        m_MessageSubtype = value;
    }


  
  
  
  protected:
    llrp_bytesToEnd_t m_Data;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdData;
//@}

    /** @brief Get accessor functions for the LLRP Data field */
    inline llrp_bytesToEnd_t
    getData (void)
    {
        return m_Data;
    }

    /** @brief Set accessor functions for the LLRP Data field */
    inline void
    setData (
      llrp_bytesToEnd_t value)
    {
        m_Data = value;
    }


  
};


/**
 ** @brief  Class Definition CGET_READER_CAPABILITIES for LLRP message GET_READER_CAPABILITIES
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=44&view=fit>LLRP Specification Section 9.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=117&view=fit>LLRP Specification Section 16.1.1</a>
  </li>
  
</ul>  

      
         
    <p>This message is sent from the Client to the Reader. The Client is able to request only a subset or all the capabilities from the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CGET_READER_CAPABILITIES : public CMessage
{
  public:
    CGET_READER_CAPABILITIES (void);
    ~CGET_READER_CAPABILITIES (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EGetReaderCapabilitiesRequestedData m_eRequestedData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdRequestedData;
//@}

    /** @brief Get accessor functions for the LLRP RequestedData field */
    inline EGetReaderCapabilitiesRequestedData
    getRequestedData (void)
    {
        return m_eRequestedData;
    }

    /** @brief Set accessor functions for the LLRP RequestedData field */
    inline void
    setRequestedData (
      EGetReaderCapabilitiesRequestedData value)
    {
        m_eRequestedData = value;
    }


  
  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CGET_READER_CAPABILITIES_RESPONSE for LLRP message GET_READER_CAPABILITIES_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=44&view=fit>LLRP Specification Section 9.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=117&view=fit>LLRP Specification Section 16.1.2</a>
  </li>
  
</ul>  

      
         
    <p>This is the response from the Reader to the GET_READER_CAPABILITIES message. The response contains the LLRPStatus Parameter and the list of parameters for the requested capabilities conveyed via RequestedData in the GET_READER_CAPABILITIES message. </p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CGET_READER_CAPABILITIES_RESPONSE : public CMessage
{
  public:
    CGET_READER_CAPABILITIES_RESPONSE (void);
    ~CGET_READER_CAPABILITIES_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


  
  
  protected:
    CGeneralDeviceCapabilities * m_pGeneralDeviceCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP GeneralDeviceCapabilities sub-parameter */  
    inline CGeneralDeviceCapabilities *
    getGeneralDeviceCapabilities (void)
    {
        return m_pGeneralDeviceCapabilities;
    }

    /** @brief Set accessor functions for the LLRP GeneralDeviceCapabilities sub-parameter */  
    EResultCode
    setGeneralDeviceCapabilities (
      CGeneralDeviceCapabilities * pValue);


  
  
  protected:
    CLLRPCapabilities * m_pLLRPCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP LLRPCapabilities sub-parameter */  
    inline CLLRPCapabilities *
    getLLRPCapabilities (void)
    {
        return m_pLLRPCapabilities;
    }

    /** @brief Set accessor functions for the LLRP LLRPCapabilities sub-parameter */  
    EResultCode
    setLLRPCapabilities (
      CLLRPCapabilities * pValue);


  
  
  protected:
    CRegulatoryCapabilities * m_pRegulatoryCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP RegulatoryCapabilities sub-parameter */  
    inline CRegulatoryCapabilities *
    getRegulatoryCapabilities (void)
    {
        return m_pRegulatoryCapabilities;
    }

    /** @brief Set accessor functions for the LLRP RegulatoryCapabilities sub-parameter */  
    EResultCode
    setRegulatoryCapabilities (
      CRegulatoryCapabilities * pValue);


  
  
  protected:
    CParameter * m_pAirProtocolLLRPCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP AirProtocolLLRPCapabilities sub-parameter */  
    inline CParameter *
    getAirProtocolLLRPCapabilities (void)
    {
        return m_pAirProtocolLLRPCapabilities;
    }

    /** @brief Set accessor functions for the LLRP AirProtocolLLRPCapabilities sub-parameter */  
    EResultCode
    setAirProtocolLLRPCapabilities (
      CParameter * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CADD_ROSPEC for LLRP message ADD_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=51&view=fit>LLRP Specification Section 10.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=117&view=fit>LLRP Specification Section 16.1.3</a>
  </li>
  
</ul>  

      
          
    <p>An ADD_ROSPEC message communicates the information of a ROSpec to the Reader. LLRP supports configuration of multiple ROSpecs. Each ROSpec is uniquely identified using a ROSpecID, generated by the Client. The ROSpec starts at the Disabled state waiting for the ENABLE_ROSPEC message for the ROSpec from the Client, upon which it transitions to the Inactive state.</p> 
  
          
    <p>The Client 
   <b>SHALL</b>
  add a ROSpec in a Disabled State - i.e., CurrentState field in the ROSpec Parameter (section 10.2.1) 
   <b>SHALL</b>
  be set to disabled. If the CurrentState value is different than disabled, an error 
   <b>SHALL</b>
  be returned in the ADD_ROSPEC_RESPONSE (e.g. P_FieldError).</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CADD_ROSPEC : public CMessage
{
  public:
    CADD_ROSPEC (void);
    ~CADD_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CROSpec * m_pROSpec;

  public:
    /** @brief Get accessor functions for the LLRP ROSpec sub-parameter */  
    inline CROSpec *
    getROSpec (void)
    {
        return m_pROSpec;
    }

    /** @brief Set accessor functions for the LLRP ROSpec sub-parameter */  
    EResultCode
    setROSpec (
      CROSpec * pValue);


};


/**
 ** @brief  Class Definition CADD_ROSPEC_RESPONSE for LLRP message ADD_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=51&view=fit>LLRP Specification Section 10.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=118&view=fit>LLRP Specification Section 16.1.4</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to an ADD_ROSPEC message. If all the parameters specified in the ADD_ROSPEC command are successfully set, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CADD_ROSPEC_RESPONSE : public CMessage
{
  public:
    CADD_ROSPEC_RESPONSE (void);
    ~CADD_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CDELETE_ROSPEC for LLRP message DELETE_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=51&view=fit>LLRP Specification Section 10.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=118&view=fit>LLRP Specification Section 16.1.5</a>
  </li>
  
</ul>  

      
          
    <p>This command is issued by the Client to the Reader. This command deletes the ROSpec at the Reader corresponding to ROSpecID passed in this message.</p> 
 
          
    <p>ROSpecID: Zero indicates to delete all ROSpecs.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDELETE_ROSPEC : public CMessage
{
  public:
    CDELETE_ROSPEC (void);
    ~CDELETE_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CDELETE_ROSPEC_RESPONSE for LLRP message DELETE_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=52&view=fit>LLRP Specification Section 10.1.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=118&view=fit>LLRP Specification Section 16.1.6</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a DELETE_ROSPEC command. If there was a ROSpec corresponding to the ROSpecID that the Reader was presently executing, and the Reader was successful in stopping that execution, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDELETE_ROSPEC_RESPONSE : public CMessage
{
  public:
    CDELETE_ROSPEC_RESPONSE (void);
    ~CDELETE_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CSTART_ROSPEC for LLRP message START_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=52&view=fit>LLRP Specification Section 10.1.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=118&view=fit>LLRP Specification Section 16.1.7</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader starts the ROSpec corresponding to ROSpecID passed in this message, if the ROSpec is in the enabled state.</p> 
  
          
    <p>ROSpecID: Zero is disallowed.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSTART_ROSPEC : public CMessage
{
  public:
    CSTART_ROSPEC (void);
    ~CSTART_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CSTART_ROSPEC_RESPONSE for LLRP message START_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=52&view=fit>LLRP Specification Section 10.1.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=119&view=fit>LLRP Specification Section 16.1.8</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a START_ROSPEC command. If there was a ROSpec corresponding to the ROSpecID in the enabled state, and the Reader was able to start executing that ROSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSTART_ROSPEC_RESPONSE : public CMessage
{
  public:
    CSTART_ROSPEC_RESPONSE (void);
    ~CSTART_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CSTOP_ROSPEC for LLRP message STOP_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=53&view=fit>LLRP Specification Section 10.1.7</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=119&view=fit>LLRP Specification Section 16.1.9</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader stops the execution of the ROSpec corresponding to the ROSpecID passed in this message. STOP_ROSPEC overrides all other priorities and stops the execution. This basically moves the ROSpec's state to Inactive. This message does not the delete the ROSpec.</p> 
  
          
    <p>ROSpecID: Zero is disallowed.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSTOP_ROSPEC : public CMessage
{
  public:
    CSTOP_ROSPEC (void);
    ~CSTOP_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CSTOP_ROSPEC_RESPONSE for LLRP message STOP_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=53&view=fit>LLRP Specification Section 10.1.8</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=119&view=fit>LLRP Specification Section 16.1.10</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a STOP_ROSPEC command. If the Reader was currently executing the ROSpec corresponding to the ROSpecID, and the Reader was able to stop executing that ROSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSTOP_ROSPEC_RESPONSE : public CMessage
{
  public:
    CSTOP_ROSPEC_RESPONSE (void);
    ~CSTOP_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CENABLE_ROSPEC for LLRP message ENABLE_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=53&view=fit>LLRP Specification Section 10.1.9</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=119&view=fit>LLRP Specification Section 16.1.11</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader moves the ROSpec corresponding to the ROSpecID passed in this message from the disabled to the enabled state.</p> 
 
          
    <p>ROSpecID:  If set to zero, all ROSpecs are enabled.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CENABLE_ROSPEC : public CMessage
{
  public:
    CENABLE_ROSPEC (void);
    ~CENABLE_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CENABLE_ROSPEC_RESPONSE for LLRP message ENABLE_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=54&view=fit>LLRP Specification Section 10.1.10</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=120&view=fit>LLRP Specification Section 16.1.12</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a ENABLE_ROSPEC command. If there was a ROSpec corresponding to the ROSpecID, and the Reader was able to enable that ROSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CENABLE_ROSPEC_RESPONSE : public CMessage
{
  public:
    CENABLE_ROSPEC_RESPONSE (void);
    ~CENABLE_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CDISABLE_ROSPEC for LLRP message DISABLE_ROSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=54&view=fit>LLRP Specification Section 10.1.11</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=120&view=fit>LLRP Specification Section 16.1.13</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader moves the ROSpec corresponding to the ROSpecID passed in this message to the disabled state.</p> 
 
          
    <p>ROSpecID:  If set to Zero, all ROSpecs are disabled.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDISABLE_ROSPEC : public CMessage
{
  public:
    CDISABLE_ROSPEC (void);
    ~CDISABLE_ROSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CDISABLE_ROSPEC_RESPONSE for LLRP message DISABLE_ROSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=54&view=fit>LLRP Specification Section 10.1.12</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=120&view=fit>LLRP Specification Section 16.1.14</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a DISABLE_ROSPEC command. If there was a ROSpec corresponding to the ROSpecID, and the Reader was able to disable that ROSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDISABLE_ROSPEC_RESPONSE : public CMessage
{
  public:
    CDISABLE_ROSPEC_RESPONSE (void);
    ~CDISABLE_ROSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CGET_ROSPECS for LLRP message GET_ROSPECS
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=54&view=fit>LLRP Specification Section 10.1.13</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=120&view=fit>LLRP Specification Section 16.1.15</a>
  </li>
  
</ul>  

      
          
    <p>This is the request from the Client to the Reader to retrieve all the ROSpecs that have been configured at the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CGET_ROSPECS : public CMessage
{
  public:
    CGET_ROSPECS (void);
    ~CGET_ROSPECS (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CGET_ROSPECS_RESPONSE for LLRP message GET_ROSPECS_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=55&view=fit>LLRP Specification Section 10.1.14</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=121&view=fit>LLRP Specification Section 16.1.16</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a GET_ROSPECS command. If there are no ROSpecs configured at the Reader, the response is just the LLRPStatus parameter with the success code. Else, a list of ROSpec parameter is returned by the Reader, along with the success code in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CGET_ROSPECS_RESPONSE : public CMessage
{
  public:
    CGET_ROSPECS_RESPONSE (void);
    ~CGET_ROSPECS_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


  
  
  protected:
    std::list<CROSpec *> m_listROSpec;

  public:
     /** @brief  Returns the first element of the ROSpec sub-parameter list*/  
    inline std::list<CROSpec *>::iterator
    beginROSpec (void)
    {
        return m_listROSpec.begin();
    }

     /** @brief  Returns the last element of the ROSpec sub-parameter list*/  
    inline std::list<CROSpec *>::iterator
    endROSpec (void)
    {
        return m_listROSpec.end();
    }

     /** @brief  Clears the LLRP ROSpec sub-parameter list*/  
    inline void
    clearROSpec (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listROSpec);
    }

     /** @brief  Count of the LLRP ROSpec sub-parameter list*/  
    inline int
    countROSpec (void)
    {
        return (int) (m_listROSpec.size());
    }

    EResultCode
     /** @brief  Add a ROSpec to the LLRP sub-parameter list*/  
    addROSpec (
      CROSpec * pValue);


};


/**
 ** @brief  Class Definition CADD_ACCESSSPEC for LLRP message ADD_ACCESSSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=60&view=fit>LLRP Specification Section 11.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=121&view=fit>LLRP Specification Section 16.1.17</a>
  </li>
  
</ul>  

      
          
    <p>This command creates a new AccessSpec at the Reader. The AccessSpec starts at the Disabled state waiting for the ENABLE_ACCESSSPEC message for the AccessSpec from the Client, upon which it transitions to the Active state. The AccessSpecID is generated by the Client.</p> 
 
          
    <p>The Client 
   <b>SHALL</b>
  add an AccessSpec in a Disabled State i.e., CurrentState field in the AccessSpec Parameter (section 11.2.1) 
   <b>SHALL</b>
  be set to false. If the CurrentState value is different than false, an error 
   <b>SHALL</b>
  be returned in the ADD_ACCESSSPEC_RESPONSE (e.g. P_FieldError).</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CADD_ACCESSSPEC : public CMessage
{
  public:
    CADD_ACCESSSPEC (void);
    ~CADD_ACCESSSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CAccessSpec * m_pAccessSpec;

  public:
    /** @brief Get accessor functions for the LLRP AccessSpec sub-parameter */  
    inline CAccessSpec *
    getAccessSpec (void)
    {
        return m_pAccessSpec;
    }

    /** @brief Set accessor functions for the LLRP AccessSpec sub-parameter */  
    EResultCode
    setAccessSpec (
      CAccessSpec * pValue);


};


/**
 ** @brief  Class Definition CADD_ACCESSSPEC_RESPONSE for LLRP message ADD_ACCESSSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=61&view=fit>LLRP Specification Section 11.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=121&view=fit>LLRP Specification Section 16.1.18</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to an ADD_ACCESSSPEC command. If the parameters passed in that ADD_ACCESSSPEC command were successfully accepted and set at the Reader, then the success code is returned in the LLRPStatus parameter. However, if the AccessSpec was not successfully created at the Reader, the Reader sends a LLRPStatus parameter describing the error in the message.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CADD_ACCESSSPEC_RESPONSE : public CMessage
{
  public:
    CADD_ACCESSSPEC_RESPONSE (void);
    ~CADD_ACCESSSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CDELETE_ACCESSSPEC for LLRP message DELETE_ACCESSSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=61&view=fit>LLRP Specification Section 11.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=122&view=fit>LLRP Specification Section 16.1.19</a>
  </li>
  
</ul>  

      
          
    <p>This command is issued by the Client to the Reader. The Reader deletes the AccessSpec corresponding to the AccessSpecId, and this AccessSpec will stop taking effect from the next inventory round.</p> 
 
          
    <p>AccessSpecID: If set to Zero, all AccessSpecs are deleted.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDELETE_ACCESSSPEC : public CMessage
{
  public:
    CDELETE_ACCESSSPEC (void);
    ~CDELETE_ACCESSSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_AccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecID field */
    inline llrp_u32_t
    getAccessSpecID (void)
    {
        return m_AccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID field */
    inline void
    setAccessSpecID (
      llrp_u32_t value)
    {
        m_AccessSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CDELETE_ACCESSSPEC_RESPONSE for LLRP message DELETE_ACCESSSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=61&view=fit>LLRP Specification Section 11.1.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=122&view=fit>LLRP Specification Section 16.1.20</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a DELETE_ACCESSSPEC command. If there was an AccessSpec at the Reader corresponding to the AccessSpecID passed in the DELETE_ACCESSSPEC command, and the Reader was successful in deleting that AccessSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDELETE_ACCESSSPEC_RESPONSE : public CMessage
{
  public:
    CDELETE_ACCESSSPEC_RESPONSE (void);
    ~CDELETE_ACCESSSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CENABLE_ACCESSSPEC for LLRP message ENABLE_ACCESSSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=62&view=fit>LLRP Specification Section 11.1.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=122&view=fit>LLRP Specification Section 16.1.21</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader moves the AccessSpec corresponding to the AccessSpecID in this message from the Disabled state to the Active state. The Reader executes this access-spec until it gets a DISABLE_ACCESSSPEC or a DELETE_ACCESSSPEC from the Client. The AccessSpec takes effect with the next (and subsequent) inventory rounds.</p> 
  
          
    <p>AccessSpecID: If set to 0, all AccessSpecs are enabled.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CENABLE_ACCESSSPEC : public CMessage
{
  public:
    CENABLE_ACCESSSPEC (void);
    ~CENABLE_ACCESSSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_AccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecID field */
    inline llrp_u32_t
    getAccessSpecID (void)
    {
        return m_AccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID field */
    inline void
    setAccessSpecID (
      llrp_u32_t value)
    {
        m_AccessSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CENABLE_ACCESSSPEC_RESPONSE for LLRP message ENABLE_ACCESSSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=62&view=fit>LLRP Specification Section 11.1.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=122&view=fit>LLRP Specification Section 16.1.22</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to an ENABLE_ACCESSSPEC command. If there was an AccessSpec corresponding to the AccessSpecID, and the Reader was able to move that AccessSpec from the disabled to the active state, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CENABLE_ACCESSSPEC_RESPONSE : public CMessage
{
  public:
    CENABLE_ACCESSSPEC_RESPONSE (void);
    ~CENABLE_ACCESSSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CDISABLE_ACCESSSPEC for LLRP message DISABLE_ACCESSSPEC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=62&view=fit>LLRP Specification Section 11.1.7</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=123&view=fit>LLRP Specification Section 16.1.23</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader. Upon receiving the message, the Reader stops the execution of the AccessSpec corresponding to AccessSpecID in this message. This basically moves the AccessSpec's state to Disabled. This message does not delete the AccessSpec. The AccessSpec will stop taking effect from the next inventory round.</p> 
 
          
    <p>AccessSpecID: If set to zero, all AccessSpecs are disabled.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDISABLE_ACCESSSPEC : public CMessage
{
  public:
    CDISABLE_ACCESSSPEC (void);
    ~CDISABLE_ACCESSSPEC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_AccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecID field */
    inline llrp_u32_t
    getAccessSpecID (void)
    {
        return m_AccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID field */
    inline void
    setAccessSpecID (
      llrp_u32_t value)
    {
        m_AccessSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CDISABLE_ACCESSSPEC_RESPONSE for LLRP message DISABLE_ACCESSSPEC_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=63&view=fit>LLRP Specification Section 11.1.8</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=123&view=fit>LLRP Specification Section 16.1.24</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a STOP_ACCESSSPEC command. If the Reader was currently executing the AccessSpec corresponding to the AccessSpecID, and the Reader was able to disable that AccessSpec, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CDISABLE_ACCESSSPEC_RESPONSE : public CMessage
{
  public:
    CDISABLE_ACCESSSPEC_RESPONSE (void);
    ~CDISABLE_ACCESSSPEC_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CGET_ACCESSSPECS for LLRP message GET_ACCESSSPECS
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=63&view=fit>LLRP Specification Section 11.1.9</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=123&view=fit>LLRP Specification Section 16.1.25</a>
  </li>
  
</ul>  

      
          
    <p>This is the request from the Client to the Reader to retrieve all the AccessSpecs that have been configured at the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CGET_ACCESSSPECS : public CMessage
{
  public:
    CGET_ACCESSSPECS (void);
    ~CGET_ACCESSSPECS (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CGET_ACCESSSPECS_RESPONSE for LLRP message GET_ACCESSSPECS_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=63&view=fit>LLRP Specification Section 11.1.10</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=123&view=fit>LLRP Specification Section 16.1.26</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a GET_ACCESSSPECS command. If there are no AccessSpecs configured at the Reader, the response is just the LLRPStatus parameter with the success code. Else, a list of (AccessSpecID, AccessSpec parameter) is returned by the Reader, along with the LLRPStatus parameter containing the success code. The order of the AccessSpecs listed in the message is normatively the order in which the AccessSpecs were created at the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CGET_ACCESSSPECS_RESPONSE : public CMessage
{
  public:
    CGET_ACCESSSPECS_RESPONSE (void);
    ~CGET_ACCESSSPECS_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


  
  
  protected:
    std::list<CAccessSpec *> m_listAccessSpec;

  public:
     /** @brief  Returns the first element of the AccessSpec sub-parameter list*/  
    inline std::list<CAccessSpec *>::iterator
    beginAccessSpec (void)
    {
        return m_listAccessSpec.begin();
    }

     /** @brief  Returns the last element of the AccessSpec sub-parameter list*/  
    inline std::list<CAccessSpec *>::iterator
    endAccessSpec (void)
    {
        return m_listAccessSpec.end();
    }

     /** @brief  Clears the LLRP AccessSpec sub-parameter list*/  
    inline void
    clearAccessSpec (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAccessSpec);
    }

     /** @brief  Count of the LLRP AccessSpec sub-parameter list*/  
    inline int
    countAccessSpec (void)
    {
        return (int) (m_listAccessSpec.size());
    }

    EResultCode
     /** @brief  Add a AccessSpec to the LLRP sub-parameter list*/  
    addAccessSpec (
      CAccessSpec * pValue);


};


/**
 ** @brief  Class Definition CGET_READER_CONFIG for LLRP message GET_READER_CONFIG
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=67&view=fit>LLRP Specification Section 12.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=126&view=fit>LLRP Specification Section 16.1.36</a>
  </li>
  
</ul>  

      
          
    <p>This command is issued by the Client to get the current configuration information of the Reader. The Requested Data passed in the command represents the parameter(s) of interest to the Client that has to be returned by the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

  
  
  
class CGET_READER_CONFIG : public CMessage
{
  public:
    CGET_READER_CONFIG (void);
    ~CGET_READER_CONFIG (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    EGetReaderConfigRequestedData m_eRequestedData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdRequestedData;
//@}

    /** @brief Get accessor functions for the LLRP RequestedData field */
    inline EGetReaderConfigRequestedData
    getRequestedData (void)
    {
        return m_eRequestedData;
    }

    /** @brief Set accessor functions for the LLRP RequestedData field */
    inline void
    setRequestedData (
      EGetReaderConfigRequestedData value)
    {
        m_eRequestedData = value;
    }


  
  
  
  protected:
    llrp_u16_t m_GPIPortNum;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIPortNum;
//@}

    /** @brief Get accessor functions for the LLRP GPIPortNum field */
    inline llrp_u16_t
    getGPIPortNum (void)
    {
        return m_GPIPortNum;
    }

    /** @brief Set accessor functions for the LLRP GPIPortNum field */
    inline void
    setGPIPortNum (
      llrp_u16_t value)
    {
        m_GPIPortNum = value;
    }


  
  
  
  protected:
    llrp_u16_t m_GPOPortNum;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPOPortNum;
//@}

    /** @brief Get accessor functions for the LLRP GPOPortNum field */
    inline llrp_u16_t
    getGPOPortNum (void)
    {
        return m_GPOPortNum;
    }

    /** @brief Set accessor functions for the LLRP GPOPortNum field */
    inline void
    setGPOPortNum (
      llrp_u16_t value)
    {
        m_GPOPortNum = value;
    }


  
  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CGET_READER_CONFIG_RESPONSE for LLRP message GET_READER_CONFIG_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=68&view=fit>LLRP Specification Section 12.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=127&view=fit>LLRP Specification Section 16.1.37</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to the GET_READER_CONFIG message. The response is the LLRPStatus Parameter and the list of configuration parameters based on the RequestedData in GET_READER_CONFIG. If the GET_READER_CONFIG message did not have any errors, the success code is returned in the LLRPStatus parameter, and in addition the requested configuration parameters are returned. If there is an error, the appropriate error code is returned in the LLRPStatus parameter. The response contains at most one instance of each configuration parameter except for two cases, which are as follows:</p> 
 
          
    <ul>
            
    <li>
    <p>If RequestedData is 0, 2 or 3, and AntennaID is set to 0 in the GET_READER_CONFIG message, the Reader 
   <b>SHALL</b>
  return one instance of AntennaProperties Parameter or AntennaConfiguration Parameter per requested antenna.</p> 
 </li>
 
            
    <li>
    <p>If RequestedData is 0 or 9 (10), and GPIPortNum (GPOPortNum) is set to 0 in the GET_READER_CONFIG message, and, if the Reader supports GPI (GPO), the Reader 
   <b>SHALL</b>
  return one instance of GPIPortCurrentState (GPOWriteData) Parameter per requested GPI Port (GPO Port).</p> 
 </li>
 
          </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CGET_READER_CONFIG_RESPONSE : public CMessage
{
  public:
    CGET_READER_CONFIG_RESPONSE (void);
    ~CGET_READER_CONFIG_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


  
  
  protected:
    CIdentification * m_pIdentification;

  public:
    /** @brief Get accessor functions for the LLRP Identification sub-parameter */  
    inline CIdentification *
    getIdentification (void)
    {
        return m_pIdentification;
    }

    /** @brief Set accessor functions for the LLRP Identification sub-parameter */  
    EResultCode
    setIdentification (
      CIdentification * pValue);


  
  
  protected:
    std::list<CAntennaProperties *> m_listAntennaProperties;

  public:
     /** @brief  Returns the first element of the AntennaProperties sub-parameter list*/  
    inline std::list<CAntennaProperties *>::iterator
    beginAntennaProperties (void)
    {
        return m_listAntennaProperties.begin();
    }

     /** @brief  Returns the last element of the AntennaProperties sub-parameter list*/  
    inline std::list<CAntennaProperties *>::iterator
    endAntennaProperties (void)
    {
        return m_listAntennaProperties.end();
    }

     /** @brief  Clears the LLRP AntennaProperties sub-parameter list*/  
    inline void
    clearAntennaProperties (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAntennaProperties);
    }

     /** @brief  Count of the LLRP AntennaProperties sub-parameter list*/  
    inline int
    countAntennaProperties (void)
    {
        return (int) (m_listAntennaProperties.size());
    }

    EResultCode
     /** @brief  Add a AntennaProperties to the LLRP sub-parameter list*/  
    addAntennaProperties (
      CAntennaProperties * pValue);


  
  
  protected:
    std::list<CAntennaConfiguration *> m_listAntennaConfiguration;

  public:
     /** @brief  Returns the first element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    beginAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.begin();
    }

     /** @brief  Returns the last element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    endAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.end();
    }

     /** @brief  Clears the LLRP AntennaConfiguration sub-parameter list*/  
    inline void
    clearAntennaConfiguration (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAntennaConfiguration);
    }

     /** @brief  Count of the LLRP AntennaConfiguration sub-parameter list*/  
    inline int
    countAntennaConfiguration (void)
    {
        return (int) (m_listAntennaConfiguration.size());
    }

    EResultCode
     /** @brief  Add a AntennaConfiguration to the LLRP sub-parameter list*/  
    addAntennaConfiguration (
      CAntennaConfiguration * pValue);


  
  
  protected:
    CReaderEventNotificationSpec * m_pReaderEventNotificationSpec;

  public:
    /** @brief Get accessor functions for the LLRP ReaderEventNotificationSpec sub-parameter */  
    inline CReaderEventNotificationSpec *
    getReaderEventNotificationSpec (void)
    {
        return m_pReaderEventNotificationSpec;
    }

    /** @brief Set accessor functions for the LLRP ReaderEventNotificationSpec sub-parameter */  
    EResultCode
    setReaderEventNotificationSpec (
      CReaderEventNotificationSpec * pValue);


  
  
  protected:
    CROReportSpec * m_pROReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP ROReportSpec sub-parameter */  
    inline CROReportSpec *
    getROReportSpec (void)
    {
        return m_pROReportSpec;
    }

    /** @brief Set accessor functions for the LLRP ROReportSpec sub-parameter */  
    EResultCode
    setROReportSpec (
      CROReportSpec * pValue);


  
  
  protected:
    CAccessReportSpec * m_pAccessReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP AccessReportSpec sub-parameter */  
    inline CAccessReportSpec *
    getAccessReportSpec (void)
    {
        return m_pAccessReportSpec;
    }

    /** @brief Set accessor functions for the LLRP AccessReportSpec sub-parameter */  
    EResultCode
    setAccessReportSpec (
      CAccessReportSpec * pValue);


  
  
  protected:
    CLLRPConfigurationStateValue * m_pLLRPConfigurationStateValue;

  public:
    /** @brief Get accessor functions for the LLRP LLRPConfigurationStateValue sub-parameter */  
    inline CLLRPConfigurationStateValue *
    getLLRPConfigurationStateValue (void)
    {
        return m_pLLRPConfigurationStateValue;
    }

    /** @brief Set accessor functions for the LLRP LLRPConfigurationStateValue sub-parameter */  
    EResultCode
    setLLRPConfigurationStateValue (
      CLLRPConfigurationStateValue * pValue);


  
  
  protected:
    CKeepaliveSpec * m_pKeepaliveSpec;

  public:
    /** @brief Get accessor functions for the LLRP KeepaliveSpec sub-parameter */  
    inline CKeepaliveSpec *
    getKeepaliveSpec (void)
    {
        return m_pKeepaliveSpec;
    }

    /** @brief Set accessor functions for the LLRP KeepaliveSpec sub-parameter */  
    EResultCode
    setKeepaliveSpec (
      CKeepaliveSpec * pValue);


  
  
  protected:
    std::list<CGPIPortCurrentState *> m_listGPIPortCurrentState;

  public:
     /** @brief  Returns the first element of the GPIPortCurrentState sub-parameter list*/  
    inline std::list<CGPIPortCurrentState *>::iterator
    beginGPIPortCurrentState (void)
    {
        return m_listGPIPortCurrentState.begin();
    }

     /** @brief  Returns the last element of the GPIPortCurrentState sub-parameter list*/  
    inline std::list<CGPIPortCurrentState *>::iterator
    endGPIPortCurrentState (void)
    {
        return m_listGPIPortCurrentState.end();
    }

     /** @brief  Clears the LLRP GPIPortCurrentState sub-parameter list*/  
    inline void
    clearGPIPortCurrentState (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listGPIPortCurrentState);
    }

     /** @brief  Count of the LLRP GPIPortCurrentState sub-parameter list*/  
    inline int
    countGPIPortCurrentState (void)
    {
        return (int) (m_listGPIPortCurrentState.size());
    }

    EResultCode
     /** @brief  Add a GPIPortCurrentState to the LLRP sub-parameter list*/  
    addGPIPortCurrentState (
      CGPIPortCurrentState * pValue);


  
  
  protected:
    std::list<CGPOWriteData *> m_listGPOWriteData;

  public:
     /** @brief  Returns the first element of the GPOWriteData sub-parameter list*/  
    inline std::list<CGPOWriteData *>::iterator
    beginGPOWriteData (void)
    {
        return m_listGPOWriteData.begin();
    }

     /** @brief  Returns the last element of the GPOWriteData sub-parameter list*/  
    inline std::list<CGPOWriteData *>::iterator
    endGPOWriteData (void)
    {
        return m_listGPOWriteData.end();
    }

     /** @brief  Clears the LLRP GPOWriteData sub-parameter list*/  
    inline void
    clearGPOWriteData (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listGPOWriteData);
    }

     /** @brief  Count of the LLRP GPOWriteData sub-parameter list*/  
    inline int
    countGPOWriteData (void)
    {
        return (int) (m_listGPOWriteData.size());
    }

    EResultCode
     /** @brief  Add a GPOWriteData to the LLRP sub-parameter list*/  
    addGPOWriteData (
      CGPOWriteData * pValue);


  
  
  protected:
    CEventsAndReports * m_pEventsAndReports;

  public:
    /** @brief Get accessor functions for the LLRP EventsAndReports sub-parameter */  
    inline CEventsAndReports *
    getEventsAndReports (void)
    {
        return m_pEventsAndReports;
    }

    /** @brief Set accessor functions for the LLRP EventsAndReports sub-parameter */  
    EResultCode
    setEventsAndReports (
      CEventsAndReports * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CSET_READER_CONFIG for LLRP message SET_READER_CONFIG
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=69&view=fit>LLRP Specification Section 12.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=127&view=fit>LLRP Specification Section 16.1.38</a>
  </li>
  
</ul>  

      
          
    <p>This command is issued by the Client to the Reader. This command sets the Reader configuration using the parameters specified in this command.  Values passed by the SET_READER_CONFIG 
   <b>SHALL</b>
  apply for the duration of the LLRP connection, or until the values are changed by additional SET_READER_CONFIG messages.</p> 
 
          
    <p>For example, ROReportSpec defines the reporting of ROReport format and trigger for a ROSpec. ROReportSpec sent as part of SET_READER_CONFIG becomes the default ROReportSpec for the Reader. A ROReportSpec sent as part of ROSpec in the ADD_ROSPEC command overrides the default value for that ROSpec. However, in cases where there is no ROReportSpec specified in a ROSpec sent as part of ADD_ROSPEC, that particular ROSpec inherits the default ROReportSpec.</p> 
 
          
    <p>The data field ResetToFactoryDefault informs the Reader to set all configurable values to factory defaults before applying the remaining parameters.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CSET_READER_CONFIG : public CMessage
{
  public:
    CSET_READER_CONFIG (void);
    ~CSET_READER_CONFIG (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_ResetToFactoryDefault;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResetToFactoryDefault;
//@}

    /** @brief Get accessor functions for the LLRP ResetToFactoryDefault field */
    inline llrp_u1_t
    getResetToFactoryDefault (void)
    {
        return m_ResetToFactoryDefault;
    }

    /** @brief Set accessor functions for the LLRP ResetToFactoryDefault field */
    inline void
    setResetToFactoryDefault (
      llrp_u1_t value)
    {
        m_ResetToFactoryDefault = value;
    }


  
  
  
  protected:
    CReaderEventNotificationSpec * m_pReaderEventNotificationSpec;

  public:
    /** @brief Get accessor functions for the LLRP ReaderEventNotificationSpec sub-parameter */  
    inline CReaderEventNotificationSpec *
    getReaderEventNotificationSpec (void)
    {
        return m_pReaderEventNotificationSpec;
    }

    /** @brief Set accessor functions for the LLRP ReaderEventNotificationSpec sub-parameter */  
    EResultCode
    setReaderEventNotificationSpec (
      CReaderEventNotificationSpec * pValue);


  
  
  protected:
    std::list<CAntennaProperties *> m_listAntennaProperties;

  public:
     /** @brief  Returns the first element of the AntennaProperties sub-parameter list*/  
    inline std::list<CAntennaProperties *>::iterator
    beginAntennaProperties (void)
    {
        return m_listAntennaProperties.begin();
    }

     /** @brief  Returns the last element of the AntennaProperties sub-parameter list*/  
    inline std::list<CAntennaProperties *>::iterator
    endAntennaProperties (void)
    {
        return m_listAntennaProperties.end();
    }

     /** @brief  Clears the LLRP AntennaProperties sub-parameter list*/  
    inline void
    clearAntennaProperties (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAntennaProperties);
    }

     /** @brief  Count of the LLRP AntennaProperties sub-parameter list*/  
    inline int
    countAntennaProperties (void)
    {
        return (int) (m_listAntennaProperties.size());
    }

    EResultCode
     /** @brief  Add a AntennaProperties to the LLRP sub-parameter list*/  
    addAntennaProperties (
      CAntennaProperties * pValue);


  
  
  protected:
    std::list<CAntennaConfiguration *> m_listAntennaConfiguration;

  public:
     /** @brief  Returns the first element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    beginAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.begin();
    }

     /** @brief  Returns the last element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    endAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.end();
    }

     /** @brief  Clears the LLRP AntennaConfiguration sub-parameter list*/  
    inline void
    clearAntennaConfiguration (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAntennaConfiguration);
    }

     /** @brief  Count of the LLRP AntennaConfiguration sub-parameter list*/  
    inline int
    countAntennaConfiguration (void)
    {
        return (int) (m_listAntennaConfiguration.size());
    }

    EResultCode
     /** @brief  Add a AntennaConfiguration to the LLRP sub-parameter list*/  
    addAntennaConfiguration (
      CAntennaConfiguration * pValue);


  
  
  protected:
    CROReportSpec * m_pROReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP ROReportSpec sub-parameter */  
    inline CROReportSpec *
    getROReportSpec (void)
    {
        return m_pROReportSpec;
    }

    /** @brief Set accessor functions for the LLRP ROReportSpec sub-parameter */  
    EResultCode
    setROReportSpec (
      CROReportSpec * pValue);


  
  
  protected:
    CAccessReportSpec * m_pAccessReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP AccessReportSpec sub-parameter */  
    inline CAccessReportSpec *
    getAccessReportSpec (void)
    {
        return m_pAccessReportSpec;
    }

    /** @brief Set accessor functions for the LLRP AccessReportSpec sub-parameter */  
    EResultCode
    setAccessReportSpec (
      CAccessReportSpec * pValue);


  
  
  protected:
    CKeepaliveSpec * m_pKeepaliveSpec;

  public:
    /** @brief Get accessor functions for the LLRP KeepaliveSpec sub-parameter */  
    inline CKeepaliveSpec *
    getKeepaliveSpec (void)
    {
        return m_pKeepaliveSpec;
    }

    /** @brief Set accessor functions for the LLRP KeepaliveSpec sub-parameter */  
    EResultCode
    setKeepaliveSpec (
      CKeepaliveSpec * pValue);


  
  
  protected:
    std::list<CGPOWriteData *> m_listGPOWriteData;

  public:
     /** @brief  Returns the first element of the GPOWriteData sub-parameter list*/  
    inline std::list<CGPOWriteData *>::iterator
    beginGPOWriteData (void)
    {
        return m_listGPOWriteData.begin();
    }

     /** @brief  Returns the last element of the GPOWriteData sub-parameter list*/  
    inline std::list<CGPOWriteData *>::iterator
    endGPOWriteData (void)
    {
        return m_listGPOWriteData.end();
    }

     /** @brief  Clears the LLRP GPOWriteData sub-parameter list*/  
    inline void
    clearGPOWriteData (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listGPOWriteData);
    }

     /** @brief  Count of the LLRP GPOWriteData sub-parameter list*/  
    inline int
    countGPOWriteData (void)
    {
        return (int) (m_listGPOWriteData.size());
    }

    EResultCode
     /** @brief  Add a GPOWriteData to the LLRP sub-parameter list*/  
    addGPOWriteData (
      CGPOWriteData * pValue);


  
  
  protected:
    std::list<CGPIPortCurrentState *> m_listGPIPortCurrentState;

  public:
     /** @brief  Returns the first element of the GPIPortCurrentState sub-parameter list*/  
    inline std::list<CGPIPortCurrentState *>::iterator
    beginGPIPortCurrentState (void)
    {
        return m_listGPIPortCurrentState.begin();
    }

     /** @brief  Returns the last element of the GPIPortCurrentState sub-parameter list*/  
    inline std::list<CGPIPortCurrentState *>::iterator
    endGPIPortCurrentState (void)
    {
        return m_listGPIPortCurrentState.end();
    }

     /** @brief  Clears the LLRP GPIPortCurrentState sub-parameter list*/  
    inline void
    clearGPIPortCurrentState (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listGPIPortCurrentState);
    }

     /** @brief  Count of the LLRP GPIPortCurrentState sub-parameter list*/  
    inline int
    countGPIPortCurrentState (void)
    {
        return (int) (m_listGPIPortCurrentState.size());
    }

    EResultCode
     /** @brief  Add a GPIPortCurrentState to the LLRP sub-parameter list*/  
    addGPIPortCurrentState (
      CGPIPortCurrentState * pValue);


  
  
  protected:
    CEventsAndReports * m_pEventsAndReports;

  public:
    /** @brief Get accessor functions for the LLRP EventsAndReports sub-parameter */  
    inline CEventsAndReports *
    getEventsAndReports (void)
    {
        return m_pEventsAndReports;
    }

    /** @brief Set accessor functions for the LLRP EventsAndReports sub-parameter */  
    EResultCode
    setEventsAndReports (
      CEventsAndReports * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CSET_READER_CONFIG_RESPONSE for LLRP message SET_READER_CONFIG_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=70&view=fit>LLRP Specification Section 12.1.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=128&view=fit>LLRP Specification Section 16.1.39</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a SET_READER_CONFIG command. If all the parameters specified in the SET_READER_CONFIG command are successfully set, then the success code is returned in the LLRPStatus parameter. If there is an error, the appropriate error code is returned in the LLRPStatus parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSET_READER_CONFIG_RESPONSE : public CMessage
{
  public:
    CSET_READER_CONFIG_RESPONSE (void);
    ~CSET_READER_CONFIG_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CCLOSE_CONNECTION for LLRP message CLOSE_CONNECTION
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=70&view=fit>LLRP Specification Section 12.1.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=128&view=fit>LLRP Specification Section 16.1.40</a>
  </li>
  
</ul>  

      
          
    <p>This command is issued by the Client to the Reader.  This command instructs the Reader to gracefully close its connection with the Client.  Under normal operating conditions, a Client 
   <b>SHALL</b>
  attempt to send this command before closing an LLRP connection.  A Client should wait briefly for the Reader to respond with a CLOSE_CONNECTION_RESPONSE.</p> 
 
          
    <p>Upon receipt of this command, the Reader 
   <b>SHALL</b>
  respond with the CLOSE_CONNECTION_REPONSE message and it should then attempt to close the connection between the Reader and Client.</p> 
 
          
    <p>Having executed a CLOSE_CONNECTION command, a Reader 
   <b>MAY</b>
  persist its configuration state as defined by the ReaderConfigurationStateValue parameter specified in section 12.2.1.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CCLOSE_CONNECTION : public CMessage
{
  public:
    CCLOSE_CONNECTION (void);
    ~CCLOSE_CONNECTION (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CCLOSE_CONNECTION_RESPONSE for LLRP message CLOSE_CONNECTION_RESPONSE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=71&view=fit>LLRP Specification Section 12.1.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=128&view=fit>LLRP Specification Section 16.1.41</a>
  </li>
  
</ul>  

      
          
    <p>This is the response by the Reader to a CLOSE_CONNECTON command from the Client.  Upon receiving a CLOSE_CONNECTION command, the Reader 
   <b>SHALL</b>
  attempt to send this response to the Client.  After attempting to send this response, the Reader 
   <b>SHALL</b>
  close its connection with the Client.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CCLOSE_CONNECTION_RESPONSE : public CMessage
{
  public:
    CCLOSE_CONNECTION_RESPONSE (void);
    ~CCLOSE_CONNECTION_RESPONSE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/**
 ** @brief  Class Definition CGET_REPORT for LLRP message GET_REPORT
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=76&view=fit>LLRP Specification Section 13.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=124&view=fit>LLRP Specification Section 16.1.29</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Client to the Reader to get the tag reports. In response to this message, the Reader 
   <b>SHALL</b>
  return tag reports accumulated.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CGET_REPORT : public CMessage
{
  public:
    CGET_REPORT (void);
    ~CGET_REPORT (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CRO_ACCESS_REPORT for LLRP message RO_ACCESS_REPORT
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=77&view=fit>LLRP Specification Section 13.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=125&view=fit>LLRP Specification Section 16.1.30</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Reader to the Client, and it contains the results of the RO and Access operations. The ROReportSpec and AccessReportSpec parameters define the contents and triggers for this message.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CRO_ACCESS_REPORT : public CMessage
{
  public:
    CRO_ACCESS_REPORT (void);
    ~CRO_ACCESS_REPORT (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    std::list<CTagReportData *> m_listTagReportData;

  public:
     /** @brief  Returns the first element of the TagReportData sub-parameter list*/  
    inline std::list<CTagReportData *>::iterator
    beginTagReportData (void)
    {
        return m_listTagReportData.begin();
    }

     /** @brief  Returns the last element of the TagReportData sub-parameter list*/  
    inline std::list<CTagReportData *>::iterator
    endTagReportData (void)
    {
        return m_listTagReportData.end();
    }

     /** @brief  Clears the LLRP TagReportData sub-parameter list*/  
    inline void
    clearTagReportData (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listTagReportData);
    }

     /** @brief  Count of the LLRP TagReportData sub-parameter list*/  
    inline int
    countTagReportData (void)
    {
        return (int) (m_listTagReportData.size());
    }

    EResultCode
     /** @brief  Add a TagReportData to the LLRP sub-parameter list*/  
    addTagReportData (
      CTagReportData * pValue);


  
  
  protected:
    std::list<CRFSurveyReportData *> m_listRFSurveyReportData;

  public:
     /** @brief  Returns the first element of the RFSurveyReportData sub-parameter list*/  
    inline std::list<CRFSurveyReportData *>::iterator
    beginRFSurveyReportData (void)
    {
        return m_listRFSurveyReportData.begin();
    }

     /** @brief  Returns the last element of the RFSurveyReportData sub-parameter list*/  
    inline std::list<CRFSurveyReportData *>::iterator
    endRFSurveyReportData (void)
    {
        return m_listRFSurveyReportData.end();
    }

     /** @brief  Clears the LLRP RFSurveyReportData sub-parameter list*/  
    inline void
    clearRFSurveyReportData (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listRFSurveyReportData);
    }

     /** @brief  Count of the LLRP RFSurveyReportData sub-parameter list*/  
    inline int
    countRFSurveyReportData (void)
    {
        return (int) (m_listRFSurveyReportData.size());
    }

    EResultCode
     /** @brief  Add a RFSurveyReportData to the LLRP sub-parameter list*/  
    addRFSurveyReportData (
      CRFSurveyReportData * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CKEEPALIVE for LLRP message KEEPALIVE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=77&view=fit>LLRP Specification Section 13.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=125&view=fit>LLRP Specification Section 16.1.31</a>
  </li>
  
</ul>  

      
          
    <p>This message is issued by the Reader to the Client. This message can be used by the Client to monitor the LLRP-layer connectivity with the Reader. The Client configures the trigger at the Reader to send the Keepalive message. The configuration is done using the KeepaliveSpec parameter (section 12.2.4).</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CKEEPALIVE : public CMessage
{
  public:
    CKEEPALIVE (void);
    ~CKEEPALIVE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CKEEPALIVE_ACK for LLRP message KEEPALIVE_ACK
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=77&view=fit>LLRP Specification Section 13.1.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=125&view=fit>LLRP Specification Section 16.1.32</a>
  </li>
  
</ul>  

      
          
    <p>A Client 
   <b>SHALL</b>
  generate a KEEPALIVE_ACK in response to each KEEPALIVE received by the reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CKEEPALIVE_ACK : public CMessage
{
  public:
    CKEEPALIVE_ACK (void);
    ~CKEEPALIVE_ACK (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CREADER_EVENT_NOTIFICATION for LLRP message READER_EVENT_NOTIFICATION
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=77&view=fit>LLRP Specification Section 13.1.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=126&view=fit>LLRP Specification Section 16.1.33</a>
  </li>
  
</ul>  

      
         
    <p>This message is issued by the Reader to the Client whenever an event that the Client subscribed to occurs. The pertinent event data is conveyed using the ReaderEventNotificationData parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CREADER_EVENT_NOTIFICATION : public CMessage
{
  public:
    CREADER_EVENT_NOTIFICATION (void);
    ~CREADER_EVENT_NOTIFICATION (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CReaderEventNotificationData * m_pReaderEventNotificationData;

  public:
    /** @brief Get accessor functions for the LLRP ReaderEventNotificationData sub-parameter */  
    inline CReaderEventNotificationData *
    getReaderEventNotificationData (void)
    {
        return m_pReaderEventNotificationData;
    }

    /** @brief Set accessor functions for the LLRP ReaderEventNotificationData sub-parameter */  
    EResultCode
    setReaderEventNotificationData (
      CReaderEventNotificationData * pValue);


};


/**
 ** @brief  Class Definition CENABLE_EVENTS_AND_REPORTS for LLRP message ENABLE_EVENTS_AND_REPORTS
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=78&view=fit>LLRP Specification Section 13.1.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=126&view=fit>LLRP Specification Section 16.1.34</a>
  </li>
  
</ul>  

      
          
    <p>This message can be issued by the Client to the Reader after a LLRP connection is established. The Client uses this message to inform the Reader that it can remove its hold on event and report messages.  Readers that are configured to hold events and reports on reconnection (See Section 12.2.6.4) respond to this message by returning the tag reports accumulated (same way they respond to GET_REPORT (See Section 13.1.1)).</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CENABLE_EVENTS_AND_REPORTS : public CMessage
{
  public:
    CENABLE_EVENTS_AND_REPORTS (void);
    ~CENABLE_EVENTS_AND_REPORTS (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CERROR_MESSAGE for LLRP message ERROR_MESSAGE
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=93&view=fit>LLRP Specification Section 14.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=126&view=fit>LLRP Specification Section 16.1.35</a>
  </li>
  
</ul>  

      
          
    <p>The Reader 
   <b>SHALL</b>
  discard the message if there is at least one error in the message, or cannot be fully processed. In addition, no portion of the message containing an error 
   <b>SHALL</b>
  be executed by the Reader. In case the message has one or more errors, the Reader 
   <b>SHALL</b>
  return at least one error parameter for one of the errors. The Reader 
   <b>MAY</b>
  return more than one error parameter, one for each error. The errors are conveyed using a combination of "generic error codes", a pointer to the culprit parameter/field, and a description of the error encoded as a string of UTF-8 characters.</p> 
 
          
    <p>Typically the errors in the LLRP defined messages are conveyed inside of the responses from the Reader. However, in cases where the message received by the Reader contains an unsupported message type, or a CUSTOM_MESSAGE with unsupported parameters or fields, the Reader 
   <b>SHALL</b>
  respond with the ERROR_MESSAGE.</p> 
 
          
    <p>When a Reader or Client receives a command or notification with a version that is not supported, the receiver 
   <b>SHALL</b>
  send an ERROR_MESSAGE in reply consisting of:  A version that is the same as the received message, the message ID that matches the received message, and an LLRPStatusParameter with the ErrorCode set to M_UnsupportedVersion. This message 
   <b>SHALL</b>
  contain no sub-parameters (such as Field Error, Parameter Error).</p> 
 
          
    <p>Readers and Clients 
   <b>SHALL</b>
  not respond to an ERROR_MESSAGE. </p> 
 
          
    <p>This message is issued by the Reader to the Client, and it contains the LLRPStatus parameter that describes the error in the message.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CERROR_MESSAGE : public CMessage
{
  public:
    CERROR_MESSAGE (void);
    ~CERROR_MESSAGE (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CLLRPStatus * m_pLLRPStatus;

  public:
    /** @brief Get accessor functions for the LLRP LLRPStatus sub-parameter */  
    inline CLLRPStatus *
    getLLRPStatus (void)
    {
        return m_pLLRPStatus;
    }

    /** @brief Set accessor functions for the LLRP LLRPStatus sub-parameter */  
    EResultCode
    setLLRPStatus (
      CLLRPStatus * pValue);


};


/*@}*/

/** 
 * \defgroup CoreParameter Core Parameter Classes
 * Classes to manipulate the parameters defined by the Core LLRP protocol
 */
/*@{*/ 

/**
 ** @brief  Class Definition CUTCTimestamp for LLRP parameter UTCTimestamp
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=37&view=fit>LLRP Specification Section 7.1.3.1.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=131&view=fit>LLRP Specification Section 16.2.2.1</a>
  </li>
  
</ul>  

      
        
    <p> The timestamps in LLRP messages or parameters can be either the uptime or the UTC time [UTC]. If a Reader has an UTC clock, all timestamps reported by the Reader 
   <b>SHALL</b>
  use an UTC timestamp parameter. If a Reader has no UTC clock capability, all timestamps reported by the Reader. 
   <b>SHALL</b>
  use the uptime parameter. </p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CUTCTimestamp : public CParameter
{
  public:
    CUTCTimestamp (void);
    ~CUTCTimestamp (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CUptime for LLRP parameter Uptime
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=37&view=fit>LLRP Specification Section 7.1.3.1.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=131&view=fit>LLRP Specification Section 16.2.2.2</a>
  </li>
  
</ul>  
          
      
         
    <p> The timestamps in LLRP messages or parameters can be either the uptime or the UTC time [UTC]. If a Reader has an UTC clock, all timestamps reported by the Reader 
   <b>SHALL</b>
  use an UTC timestamp parameter. If a Reader has no UTC clock capability, all timestamps reported by the Reader 
   <b>SHALL</b>
  use the uptime parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CUptime : public CParameter
{
  public:
    CUptime (void);
    ~CUptime (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CCustom for LLRP parameter Custom
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=42&view=fit>LLRP Specification Section 8.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=152&view=fit>LLRP Specification Section 16.2.9</a>
  </li>
  
</ul>  
                
      
         
    <p>Certain Messages and Parameter Sets within LLRP allow for the insertion of vendor defined parameters</p> 
 
              
    <p>Clients 
   <b>SHALL</b>
  accept messages (except for CUSTOM_MESSAGE) that contain custom parameters but 
   <b>MAY</b>
  ignore all custom parameters within these messages. Readers 
   <b>SHALL</b>
  accept messages (except for CUSTOM_MESSAGE) that contain custom parameters and 
   <b>SHALL</b>
  return an error when such parameters are unsupported. </p> 
     
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CCustom : public CParameter
{
  public:
    CCustom (void);
    ~CCustom (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_VendorIdentifier;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdVendorIdentifier;
//@}

    /** @brief Get accessor functions for the LLRP VendorIdentifier field */
    inline llrp_u32_t
    getVendorIdentifier (void)
    {
        return m_VendorIdentifier;
    }

    /** @brief Set accessor functions for the LLRP VendorIdentifier field */
    inline void
    setVendorIdentifier (
      llrp_u32_t value)
    {
        m_VendorIdentifier = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ParameterSubtype;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdParameterSubtype;
//@}

    /** @brief Get accessor functions for the LLRP ParameterSubtype field */
    inline llrp_u32_t
    getParameterSubtype (void)
    {
        return m_ParameterSubtype;
    }

    /** @brief Set accessor functions for the LLRP ParameterSubtype field */
    inline void
    setParameterSubtype (
      llrp_u32_t value)
    {
        m_ParameterSubtype = value;
    }


  
  
  
  protected:
    llrp_bytesToEnd_t m_Data;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdData;
//@}

    /** @brief Get accessor functions for the LLRP Data field */
    inline llrp_bytesToEnd_t
    getData (void)
    {
        return m_Data;
    }

    /** @brief Set accessor functions for the LLRP Data field */
    inline void
    setData (
      llrp_bytesToEnd_t value)
    {
        m_Data = value;
    }


  
};


/**
 ** @brief  Class Definition CGeneralDeviceCapabilities for LLRP parameter GeneralDeviceCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=45&view=fit>LLRP Specification Section 9.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=131&view=fit>LLRP Specification Section 16.2.3.1</a>
  </li>
  
</ul>  

      
         
    <p>This parameter carries the general capabilities of the device like supported air protocols, version of the Reader firmware, device hardware and software information, and receive sensitivity table. </p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CGeneralDeviceCapabilities : public CParameter
{
  public:
    CGeneralDeviceCapabilities (void);
    ~CGeneralDeviceCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_MaxNumberOfAntennaSupported;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumberOfAntennaSupported;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumberOfAntennaSupported field */
    inline llrp_u16_t
    getMaxNumberOfAntennaSupported (void)
    {
        return m_MaxNumberOfAntennaSupported;
    }

    /** @brief Set accessor functions for the LLRP MaxNumberOfAntennaSupported field */
    inline void
    setMaxNumberOfAntennaSupported (
      llrp_u16_t value)
    {
        m_MaxNumberOfAntennaSupported = value;
    }


  
  
  
  protected:
    llrp_u1_t m_CanSetAntennaProperties;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanSetAntennaProperties;
//@}

    /** @brief Get accessor functions for the LLRP CanSetAntennaProperties field */
    inline llrp_u1_t
    getCanSetAntennaProperties (void)
    {
        return m_CanSetAntennaProperties;
    }

    /** @brief Set accessor functions for the LLRP CanSetAntennaProperties field */
    inline void
    setCanSetAntennaProperties (
      llrp_u1_t value)
    {
        m_CanSetAntennaProperties = value;
    }


  
  
  
  protected:
    llrp_u1_t m_HasUTCClockCapability;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHasUTCClockCapability;
//@}

    /** @brief Get accessor functions for the LLRP HasUTCClockCapability field */
    inline llrp_u1_t
    getHasUTCClockCapability (void)
    {
        return m_HasUTCClockCapability;
    }

    /** @brief Set accessor functions for the LLRP HasUTCClockCapability field */
    inline void
    setHasUTCClockCapability (
      llrp_u1_t value)
    {
        m_HasUTCClockCapability = value;
    }


  
  
  
  protected:
    llrp_u32_t m_DeviceManufacturerName;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDeviceManufacturerName;
//@}

    /** @brief Get accessor functions for the LLRP DeviceManufacturerName field */
    inline llrp_u32_t
    getDeviceManufacturerName (void)
    {
        return m_DeviceManufacturerName;
    }

    /** @brief Set accessor functions for the LLRP DeviceManufacturerName field */
    inline void
    setDeviceManufacturerName (
      llrp_u32_t value)
    {
        m_DeviceManufacturerName = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ModelName;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdModelName;
//@}

    /** @brief Get accessor functions for the LLRP ModelName field */
    inline llrp_u32_t
    getModelName (void)
    {
        return m_ModelName;
    }

    /** @brief Set accessor functions for the LLRP ModelName field */
    inline void
    setModelName (
      llrp_u32_t value)
    {
        m_ModelName = value;
    }


  
  
  
  protected:
    llrp_utf8v_t m_ReaderFirmwareVersion;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReaderFirmwareVersion;
//@}

    /** @brief Get accessor functions for the LLRP ReaderFirmwareVersion field */
    inline llrp_utf8v_t
    getReaderFirmwareVersion (void)
    {
        return m_ReaderFirmwareVersion;
    }

    /** @brief Set accessor functions for the LLRP ReaderFirmwareVersion field */
    inline void
    setReaderFirmwareVersion (
      llrp_utf8v_t value)
    {
        m_ReaderFirmwareVersion = value;
    }


  
  
  
  protected:
    std::list<CReceiveSensitivityTableEntry *> m_listReceiveSensitivityTableEntry;

  public:
     /** @brief  Returns the first element of the ReceiveSensitivityTableEntry sub-parameter list*/  
    inline std::list<CReceiveSensitivityTableEntry *>::iterator
    beginReceiveSensitivityTableEntry (void)
    {
        return m_listReceiveSensitivityTableEntry.begin();
    }

     /** @brief  Returns the last element of the ReceiveSensitivityTableEntry sub-parameter list*/  
    inline std::list<CReceiveSensitivityTableEntry *>::iterator
    endReceiveSensitivityTableEntry (void)
    {
        return m_listReceiveSensitivityTableEntry.end();
    }

     /** @brief  Clears the LLRP ReceiveSensitivityTableEntry sub-parameter list*/  
    inline void
    clearReceiveSensitivityTableEntry (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listReceiveSensitivityTableEntry);
    }

     /** @brief  Count of the LLRP ReceiveSensitivityTableEntry sub-parameter list*/  
    inline int
    countReceiveSensitivityTableEntry (void)
    {
        return (int) (m_listReceiveSensitivityTableEntry.size());
    }

    EResultCode
     /** @brief  Add a ReceiveSensitivityTableEntry to the LLRP sub-parameter list*/  
    addReceiveSensitivityTableEntry (
      CReceiveSensitivityTableEntry * pValue);


  
  
  protected:
    std::list<CPerAntennaReceiveSensitivityRange *> m_listPerAntennaReceiveSensitivityRange;

  public:
     /** @brief  Returns the first element of the PerAntennaReceiveSensitivityRange sub-parameter list*/  
    inline std::list<CPerAntennaReceiveSensitivityRange *>::iterator
    beginPerAntennaReceiveSensitivityRange (void)
    {
        return m_listPerAntennaReceiveSensitivityRange.begin();
    }

     /** @brief  Returns the last element of the PerAntennaReceiveSensitivityRange sub-parameter list*/  
    inline std::list<CPerAntennaReceiveSensitivityRange *>::iterator
    endPerAntennaReceiveSensitivityRange (void)
    {
        return m_listPerAntennaReceiveSensitivityRange.end();
    }

     /** @brief  Clears the LLRP PerAntennaReceiveSensitivityRange sub-parameter list*/  
    inline void
    clearPerAntennaReceiveSensitivityRange (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listPerAntennaReceiveSensitivityRange);
    }

     /** @brief  Count of the LLRP PerAntennaReceiveSensitivityRange sub-parameter list*/  
    inline int
    countPerAntennaReceiveSensitivityRange (void)
    {
        return (int) (m_listPerAntennaReceiveSensitivityRange.size());
    }

    EResultCode
     /** @brief  Add a PerAntennaReceiveSensitivityRange to the LLRP sub-parameter list*/  
    addPerAntennaReceiveSensitivityRange (
      CPerAntennaReceiveSensitivityRange * pValue);


  
  
  protected:
    CGPIOCapabilities * m_pGPIOCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP GPIOCapabilities sub-parameter */  
    inline CGPIOCapabilities *
    getGPIOCapabilities (void)
    {
        return m_pGPIOCapabilities;
    }

    /** @brief Set accessor functions for the LLRP GPIOCapabilities sub-parameter */  
    EResultCode
    setGPIOCapabilities (
      CGPIOCapabilities * pValue);


  
  
  protected:
    std::list<CPerAntennaAirProtocol *> m_listPerAntennaAirProtocol;

  public:
     /** @brief  Returns the first element of the PerAntennaAirProtocol sub-parameter list*/  
    inline std::list<CPerAntennaAirProtocol *>::iterator
    beginPerAntennaAirProtocol (void)
    {
        return m_listPerAntennaAirProtocol.begin();
    }

     /** @brief  Returns the last element of the PerAntennaAirProtocol sub-parameter list*/  
    inline std::list<CPerAntennaAirProtocol *>::iterator
    endPerAntennaAirProtocol (void)
    {
        return m_listPerAntennaAirProtocol.end();
    }

     /** @brief  Clears the LLRP PerAntennaAirProtocol sub-parameter list*/  
    inline void
    clearPerAntennaAirProtocol (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listPerAntennaAirProtocol);
    }

     /** @brief  Count of the LLRP PerAntennaAirProtocol sub-parameter list*/  
    inline int
    countPerAntennaAirProtocol (void)
    {
        return (int) (m_listPerAntennaAirProtocol.size());
    }

    EResultCode
     /** @brief  Add a PerAntennaAirProtocol to the LLRP sub-parameter list*/  
    addPerAntennaAirProtocol (
      CPerAntennaAirProtocol * pValue);


};


/**
 ** @brief  Class Definition CReceiveSensitivityTableEntry for LLRP parameter ReceiveSensitivityTableEntry
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=45&view=fit>LLRP Specification Section 9.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=132&view=fit>LLRP Specification Section 16.2.3.1.1</a>
  </li>
  
</ul>  

      
         
    <p>This parameter specifies the index into the Receive Sensitivity Table for a receive sensitivity value. The receive sensitivity is expressed in dB and the value is relative to the maximum sensitivity. If the Reader does not allow control of receive sensitivity, a table of one entry is returned, the entry having the value of zero.</p> 
 
          
    <p>If the Reader allows control of receive sensitivity and the Reader also supports multiple antennas where the antennas can have different receive sensitivity values, then the Receive Sensitivity Table should be a set of values representing the union of sensitivity values for all antennas.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CReceiveSensitivityTableEntry : public CParameter
{
  public:
    CReceiveSensitivityTableEntry (void);
    ~CReceiveSensitivityTableEntry (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_Index;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdIndex;
//@}

    /** @brief Get accessor functions for the LLRP Index field */
    inline llrp_u16_t
    getIndex (void)
    {
        return m_Index;
    }

    /** @brief Set accessor functions for the LLRP Index field */
    inline void
    setIndex (
      llrp_u16_t value)
    {
        m_Index = value;
    }


  
  
  
  protected:
    llrp_s16_t m_ReceiveSensitivityValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReceiveSensitivityValue;
//@}

    /** @brief Get accessor functions for the LLRP ReceiveSensitivityValue field */
    inline llrp_s16_t
    getReceiveSensitivityValue (void)
    {
        return m_ReceiveSensitivityValue;
    }

    /** @brief Set accessor functions for the LLRP ReceiveSensitivityValue field */
    inline void
    setReceiveSensitivityValue (
      llrp_s16_t value)
    {
        m_ReceiveSensitivityValue = value;
    }


  
};


/**
 ** @brief  Class Definition CPerAntennaReceiveSensitivityRange for LLRP parameter PerAntennaReceiveSensitivityRange
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=46&view=fit>LLRP Specification Section 9.2.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=132&view=fit>LLRP Specification Section 16.2.3.1.2</a>
  </li>
  
</ul>  

      
         
    <p>For a particular antenna, this parameter specifies the Reader's valid index range in the Receive Sensitivity Table.  A Reader should report this parameter if the Reader allows control of receive sensitivity (i.e., the Reader reports a Receive Sensitivity Table with more than one entry) and the Reader supports multiple antennas where the antennas can have different receive sensitivity values.</p> 
 
          
    <p>If this parameter is omitted, then the Client 
   <b>SHALL</b>
  assume that for all of the Reader's antennas the index range is the same as in the Receive Sensitivity Table.</p> 
          
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CPerAntennaReceiveSensitivityRange : public CParameter
{
  public:
    CPerAntennaReceiveSensitivityRange (void);
    ~CPerAntennaReceiveSensitivityRange (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_ReceiveSensitivityIndexMin;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReceiveSensitivityIndexMin;
//@}

    /** @brief Get accessor functions for the LLRP ReceiveSensitivityIndexMin field */
    inline llrp_u16_t
    getReceiveSensitivityIndexMin (void)
    {
        return m_ReceiveSensitivityIndexMin;
    }

    /** @brief Set accessor functions for the LLRP ReceiveSensitivityIndexMin field */
    inline void
    setReceiveSensitivityIndexMin (
      llrp_u16_t value)
    {
        m_ReceiveSensitivityIndexMin = value;
    }


  
  
  
  protected:
    llrp_u16_t m_ReceiveSensitivityIndexMax;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReceiveSensitivityIndexMax;
//@}

    /** @brief Get accessor functions for the LLRP ReceiveSensitivityIndexMax field */
    inline llrp_u16_t
    getReceiveSensitivityIndexMax (void)
    {
        return m_ReceiveSensitivityIndexMax;
    }

    /** @brief Set accessor functions for the LLRP ReceiveSensitivityIndexMax field */
    inline void
    setReceiveSensitivityIndexMax (
      llrp_u16_t value)
    {
        m_ReceiveSensitivityIndexMax = value;
    }


  
};


/**
 ** @brief  Class Definition CPerAntennaAirProtocol for LLRP parameter PerAntennaAirProtocol
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=46&view=fit>LLRP Specification Section 9.2.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=132&view=fit>LLRP Specification Section 16.2.3.1.3</a>
  </li>
  
</ul>  

      
         
    <p>Describes the air-protocols supporter on a per-antenna basis.</p> 
 
       
  <HR>

    
    
    
  
 **/

  
  
  
class CPerAntennaAirProtocol : public CParameter
{
  public:
    CPerAntennaAirProtocol (void);
    ~CPerAntennaAirProtocol (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    llrp_u8v_t m_ProtocolID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdProtocolID;
//@}

    /** @brief Get accessor functions for the LLRP ProtocolID field */
    inline llrp_u8v_t
    getProtocolID (void)
    {
        return m_ProtocolID;
    }

    /** @brief Set accessor functions for the LLRP ProtocolID field */
    inline void
    setProtocolID (
      llrp_u8v_t value)
    {
        m_ProtocolID = value;
    }


  
};


/**
 ** @brief  Class Definition CGPIOCapabilities for LLRP parameter GPIOCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=47&view=fit>LLRP Specification Section 9.2.1.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=133&view=fit>LLRP Specification Section 16.2.3.1.4</a>
  </li>
  
</ul>  

      
         
    <p>This parameter describes the GPIO capabilities of the Reader. A value of zero for NumGPIs indicates that the Reader does not have general purpose inputs. A value of zero for NumGPOs indicates that the Reader does not have general purpose outputs.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CGPIOCapabilities : public CParameter
{
  public:
    CGPIOCapabilities (void);
    ~CGPIOCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_NumGPIs;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumGPIs;
//@}

    /** @brief Get accessor functions for the LLRP NumGPIs field */
    inline llrp_u16_t
    getNumGPIs (void)
    {
        return m_NumGPIs;
    }

    /** @brief Set accessor functions for the LLRP NumGPIs field */
    inline void
    setNumGPIs (
      llrp_u16_t value)
    {
        m_NumGPIs = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumGPOs;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumGPOs;
//@}

    /** @brief Get accessor functions for the LLRP NumGPOs field */
    inline llrp_u16_t
    getNumGPOs (void)
    {
        return m_NumGPOs;
    }

    /** @brief Set accessor functions for the LLRP NumGPOs field */
    inline void
    setNumGPOs (
      llrp_u16_t value)
    {
        m_NumGPOs = value;
    }


  
};


/**
 ** @brief  Class Definition CLLRPCapabilities for LLRP parameter LLRPCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=47&view=fit>LLRP Specification Section 9.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=133&view=fit>LLRP Specification Section 16.2.3.2</a>
  </li>
  
</ul>  

      
         
    <p>This parameter describes the LLRP protocol capabilities of the Reader. These include optional LLRP commands and parameters, capacities of data structures used in LLRP operations, and air protocol specific capabilities used by LLRP.</p> 
 
          
    <p>Readers 
   <b>MAY</b>
  support RFSurvey, 
   <b>MAY</b>
  support tag inventory state aware singulation, 
   <b>MAY</b>
  support UTC clocks, 
   <b>MAY</b>
  support buffer fill warning reports, 
   <b>MAY</b>
  support EventAndReportHolding upon reconnect, and 
   <b>MAY</b>
  support ClientRequestOpspec. Readers 
   <b>SHALL</b>
  support at least one ROSpec, one AISpec per ROSpec, one InventoryParameterSpec per AISpec, one AccessSpec, and one OpSpec per AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CLLRPCapabilities : public CParameter
{
  public:
    CLLRPCapabilities (void);
    ~CLLRPCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_CanDoRFSurvey;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanDoRFSurvey;
//@}

    /** @brief Get accessor functions for the LLRP CanDoRFSurvey field */
    inline llrp_u1_t
    getCanDoRFSurvey (void)
    {
        return m_CanDoRFSurvey;
    }

    /** @brief Set accessor functions for the LLRP CanDoRFSurvey field */
    inline void
    setCanDoRFSurvey (
      llrp_u1_t value)
    {
        m_CanDoRFSurvey = value;
    }


  
  
  
  protected:
    llrp_u1_t m_CanReportBufferFillWarning;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanReportBufferFillWarning;
//@}

    /** @brief Get accessor functions for the LLRP CanReportBufferFillWarning field */
    inline llrp_u1_t
    getCanReportBufferFillWarning (void)
    {
        return m_CanReportBufferFillWarning;
    }

    /** @brief Set accessor functions for the LLRP CanReportBufferFillWarning field */
    inline void
    setCanReportBufferFillWarning (
      llrp_u1_t value)
    {
        m_CanReportBufferFillWarning = value;
    }


  
  
  
  protected:
    llrp_u1_t m_SupportsClientRequestOpSpec;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSupportsClientRequestOpSpec;
//@}

    /** @brief Get accessor functions for the LLRP SupportsClientRequestOpSpec field */
    inline llrp_u1_t
    getSupportsClientRequestOpSpec (void)
    {
        return m_SupportsClientRequestOpSpec;
    }

    /** @brief Set accessor functions for the LLRP SupportsClientRequestOpSpec field */
    inline void
    setSupportsClientRequestOpSpec (
      llrp_u1_t value)
    {
        m_SupportsClientRequestOpSpec = value;
    }


  
  
  
  protected:
    llrp_u1_t m_CanDoTagInventoryStateAwareSingulation;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanDoTagInventoryStateAwareSingulation;
//@}

    /** @brief Get accessor functions for the LLRP CanDoTagInventoryStateAwareSingulation field */
    inline llrp_u1_t
    getCanDoTagInventoryStateAwareSingulation (void)
    {
        return m_CanDoTagInventoryStateAwareSingulation;
    }

    /** @brief Set accessor functions for the LLRP CanDoTagInventoryStateAwareSingulation field */
    inline void
    setCanDoTagInventoryStateAwareSingulation (
      llrp_u1_t value)
    {
        m_CanDoTagInventoryStateAwareSingulation = value;
    }


  
  
  
  protected:
    llrp_u1_t m_SupportsEventAndReportHolding;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSupportsEventAndReportHolding;
//@}

    /** @brief Get accessor functions for the LLRP SupportsEventAndReportHolding field */
    inline llrp_u1_t
    getSupportsEventAndReportHolding (void)
    {
        return m_SupportsEventAndReportHolding;
    }

    /** @brief Set accessor functions for the LLRP SupportsEventAndReportHolding field */
    inline void
    setSupportsEventAndReportHolding (
      llrp_u1_t value)
    {
        m_SupportsEventAndReportHolding = value;
    }


  
  
  
  protected:
    llrp_u8_t m_MaxNumPriorityLevelsSupported;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumPriorityLevelsSupported;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumPriorityLevelsSupported field */
    inline llrp_u8_t
    getMaxNumPriorityLevelsSupported (void)
    {
        return m_MaxNumPriorityLevelsSupported;
    }

    /** @brief Set accessor functions for the LLRP MaxNumPriorityLevelsSupported field */
    inline void
    setMaxNumPriorityLevelsSupported (
      llrp_u8_t value)
    {
        m_MaxNumPriorityLevelsSupported = value;
    }


  
  
  
  protected:
    llrp_u16_t m_ClientRequestOpSpecTimeout;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdClientRequestOpSpecTimeout;
//@}

    /** @brief Get accessor functions for the LLRP ClientRequestOpSpecTimeout field */
    inline llrp_u16_t
    getClientRequestOpSpecTimeout (void)
    {
        return m_ClientRequestOpSpecTimeout;
    }

    /** @brief Set accessor functions for the LLRP ClientRequestOpSpecTimeout field */
    inline void
    setClientRequestOpSpecTimeout (
      llrp_u16_t value)
    {
        m_ClientRequestOpSpecTimeout = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxNumROSpecs;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumROSpecs;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumROSpecs field */
    inline llrp_u32_t
    getMaxNumROSpecs (void)
    {
        return m_MaxNumROSpecs;
    }

    /** @brief Set accessor functions for the LLRP MaxNumROSpecs field */
    inline void
    setMaxNumROSpecs (
      llrp_u32_t value)
    {
        m_MaxNumROSpecs = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxNumSpecsPerROSpec;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumSpecsPerROSpec;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumSpecsPerROSpec field */
    inline llrp_u32_t
    getMaxNumSpecsPerROSpec (void)
    {
        return m_MaxNumSpecsPerROSpec;
    }

    /** @brief Set accessor functions for the LLRP MaxNumSpecsPerROSpec field */
    inline void
    setMaxNumSpecsPerROSpec (
      llrp_u32_t value)
    {
        m_MaxNumSpecsPerROSpec = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxNumInventoryParameterSpecsPerAISpec;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumInventoryParameterSpecsPerAISpec;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumInventoryParameterSpecsPerAISpec field */
    inline llrp_u32_t
    getMaxNumInventoryParameterSpecsPerAISpec (void)
    {
        return m_MaxNumInventoryParameterSpecsPerAISpec;
    }

    /** @brief Set accessor functions for the LLRP MaxNumInventoryParameterSpecsPerAISpec field */
    inline void
    setMaxNumInventoryParameterSpecsPerAISpec (
      llrp_u32_t value)
    {
        m_MaxNumInventoryParameterSpecsPerAISpec = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxNumAccessSpecs;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumAccessSpecs;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumAccessSpecs field */
    inline llrp_u32_t
    getMaxNumAccessSpecs (void)
    {
        return m_MaxNumAccessSpecs;
    }

    /** @brief Set accessor functions for the LLRP MaxNumAccessSpecs field */
    inline void
    setMaxNumAccessSpecs (
      llrp_u32_t value)
    {
        m_MaxNumAccessSpecs = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxNumOpSpecsPerAccessSpec;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumOpSpecsPerAccessSpec;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumOpSpecsPerAccessSpec field */
    inline llrp_u32_t
    getMaxNumOpSpecsPerAccessSpec (void)
    {
        return m_MaxNumOpSpecsPerAccessSpec;
    }

    /** @brief Set accessor functions for the LLRP MaxNumOpSpecsPerAccessSpec field */
    inline void
    setMaxNumOpSpecsPerAccessSpec (
      llrp_u32_t value)
    {
        m_MaxNumOpSpecsPerAccessSpec = value;
    }


  
};


/**
 ** @brief  Class Definition CRegulatoryCapabilities for LLRP parameter RegulatoryCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=48&view=fit>LLRP Specification Section 9.2.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=133&view=fit>LLRP Specification Section 16.2.3.4</a>
  </li>
  
</ul>  

      
         
    <p>This parameter carries the RF regulation specific attributes. They include regulatory standard, frequency band information, power levels supported, frequencies supported, and any air protocol specific values that are determined based on regulatory restriction. </p> 
 
          
    <p> The regulatory standard is encoded using two Integer fields, (Country Code, Communications standard) and it specifies the current operational regulatory mode of the device.  This should not be used to reflect the ability to operate in regulatory environments which require configuration different from the current. This version of the LLRP protocol will have support for only the UHF band. </p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CRegulatoryCapabilities : public CParameter
{
  public:
    CRegulatoryCapabilities (void);
    ~CRegulatoryCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_CountryCode;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCountryCode;
//@}

    /** @brief Get accessor functions for the LLRP CountryCode field */
    inline llrp_u16_t
    getCountryCode (void)
    {
        return m_CountryCode;
    }

    /** @brief Set accessor functions for the LLRP CountryCode field */
    inline void
    setCountryCode (
      llrp_u16_t value)
    {
        m_CountryCode = value;
    }


  
  
  
  protected:
    ECommunicationsStandard m_eCommunicationsStandard;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCommunicationsStandard;
//@}

    /** @brief Get accessor functions for the LLRP CommunicationsStandard field */
    inline ECommunicationsStandard
    getCommunicationsStandard (void)
    {
        return m_eCommunicationsStandard;
    }

    /** @brief Set accessor functions for the LLRP CommunicationsStandard field */
    inline void
    setCommunicationsStandard (
      ECommunicationsStandard value)
    {
        m_eCommunicationsStandard = value;
    }


  
  
  
  protected:
    CUHFBandCapabilities * m_pUHFBandCapabilities;

  public:
    /** @brief Get accessor functions for the LLRP UHFBandCapabilities sub-parameter */  
    inline CUHFBandCapabilities *
    getUHFBandCapabilities (void)
    {
        return m_pUHFBandCapabilities;
    }

    /** @brief Set accessor functions for the LLRP UHFBandCapabilities sub-parameter */  
    EResultCode
    setUHFBandCapabilities (
      CUHFBandCapabilities * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CUHFBandCapabilities for LLRP parameter UHFBandCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=49&view=fit>LLRP Specification Section 9.2.4.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=134&view=fit>LLRP Specification Section 16.2.3.4.1</a>
  </li>
  
</ul>  

      
         
    <p>Describes the frequency, power, and air-protocol capabilities for the regulatory region.</p> 
 
       
  <HR>

    
    
    
    
  
 **/

  
  
  
class CUHFBandCapabilities : public CParameter
{
  public:
    CUHFBandCapabilities (void);
    ~CUHFBandCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    std::list<CTransmitPowerLevelTableEntry *> m_listTransmitPowerLevelTableEntry;

  public:
     /** @brief  Returns the first element of the TransmitPowerLevelTableEntry sub-parameter list*/  
    inline std::list<CTransmitPowerLevelTableEntry *>::iterator
    beginTransmitPowerLevelTableEntry (void)
    {
        return m_listTransmitPowerLevelTableEntry.begin();
    }

     /** @brief  Returns the last element of the TransmitPowerLevelTableEntry sub-parameter list*/  
    inline std::list<CTransmitPowerLevelTableEntry *>::iterator
    endTransmitPowerLevelTableEntry (void)
    {
        return m_listTransmitPowerLevelTableEntry.end();
    }

     /** @brief  Clears the LLRP TransmitPowerLevelTableEntry sub-parameter list*/  
    inline void
    clearTransmitPowerLevelTableEntry (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listTransmitPowerLevelTableEntry);
    }

     /** @brief  Count of the LLRP TransmitPowerLevelTableEntry sub-parameter list*/  
    inline int
    countTransmitPowerLevelTableEntry (void)
    {
        return (int) (m_listTransmitPowerLevelTableEntry.size());
    }

    EResultCode
     /** @brief  Add a TransmitPowerLevelTableEntry to the LLRP sub-parameter list*/  
    addTransmitPowerLevelTableEntry (
      CTransmitPowerLevelTableEntry * pValue);


  
  
  protected:
    CFrequencyInformation * m_pFrequencyInformation;

  public:
    /** @brief Get accessor functions for the LLRP FrequencyInformation sub-parameter */  
    inline CFrequencyInformation *
    getFrequencyInformation (void)
    {
        return m_pFrequencyInformation;
    }

    /** @brief Set accessor functions for the LLRP FrequencyInformation sub-parameter */  
    EResultCode
    setFrequencyInformation (
      CFrequencyInformation * pValue);


  
  
  protected:
    std::list<CParameter *> m_listAirProtocolUHFRFModeTable;

  public:
     /** @brief  Returns the first element of the AirProtocolUHFRFModeTable sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAirProtocolUHFRFModeTable (void)
    {
        return m_listAirProtocolUHFRFModeTable.begin();
    }

     /** @brief  Returns the last element of the AirProtocolUHFRFModeTable sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAirProtocolUHFRFModeTable (void)
    {
        return m_listAirProtocolUHFRFModeTable.end();
    }

     /** @brief  Clears the LLRP AirProtocolUHFRFModeTable sub-parameter list*/  
    inline void
    clearAirProtocolUHFRFModeTable (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAirProtocolUHFRFModeTable);
    }

     /** @brief  Count of the LLRP AirProtocolUHFRFModeTable sub-parameter list*/  
    inline int
    countAirProtocolUHFRFModeTable (void)
    {
        return (int) (m_listAirProtocolUHFRFModeTable.size());
    }

    EResultCode
     /** @brief  Add a AirProtocolUHFRFModeTable to the LLRP sub-parameter list*/  
    addAirProtocolUHFRFModeTable (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CTransmitPowerLevelTableEntry for LLRP parameter TransmitPowerLevelTableEntry
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=49&view=fit>LLRP Specification Section 9.2.4.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=134&view=fit>LLRP Specification Section 16.2.3.4.1.1</a>
  </li>
  
</ul>  

      
         
    <p>This parameter specifies the index into the TransmitPowerLevelTable for a transmit power value. The transmit power is expressed in dBm*100 to allow fractional dBm representation and is the conducted power at the connector of the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CTransmitPowerLevelTableEntry : public CParameter
{
  public:
    CTransmitPowerLevelTableEntry (void);
    ~CTransmitPowerLevelTableEntry (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_Index;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdIndex;
//@}

    /** @brief Get accessor functions for the LLRP Index field */
    inline llrp_u16_t
    getIndex (void)
    {
        return m_Index;
    }

    /** @brief Set accessor functions for the LLRP Index field */
    inline void
    setIndex (
      llrp_u16_t value)
    {
        m_Index = value;
    }


  
  
  
  protected:
    llrp_s16_t m_TransmitPowerValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTransmitPowerValue;
//@}

    /** @brief Get accessor functions for the LLRP TransmitPowerValue field */
    inline llrp_s16_t
    getTransmitPowerValue (void)
    {
        return m_TransmitPowerValue;
    }

    /** @brief Set accessor functions for the LLRP TransmitPowerValue field */
    inline void
    setTransmitPowerValue (
      llrp_s16_t value)
    {
        m_TransmitPowerValue = value;
    }


  
};


/**
 ** @brief  Class Definition CFrequencyInformation for LLRP parameter FrequencyInformation
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=50&view=fit>LLRP Specification Section 9.2.4.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=134&view=fit>LLRP Specification Section 16.2.3.4.1.2</a>
  </li>
  
</ul>  

      
         
    <p>Describes the fixed frequency or hopping frequencies supported in this UHFBand.</p> 
 
       
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CFrequencyInformation : public CParameter
{
  public:
    CFrequencyInformation (void);
    ~CFrequencyInformation (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_Hopping;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHopping;
//@}

    /** @brief Get accessor functions for the LLRP Hopping field */
    inline llrp_u1_t
    getHopping (void)
    {
        return m_Hopping;
    }

    /** @brief Set accessor functions for the LLRP Hopping field */
    inline void
    setHopping (
      llrp_u1_t value)
    {
        m_Hopping = value;
    }


  
  
  
  protected:
    std::list<CFrequencyHopTable *> m_listFrequencyHopTable;

  public:
     /** @brief  Returns the first element of the FrequencyHopTable sub-parameter list*/  
    inline std::list<CFrequencyHopTable *>::iterator
    beginFrequencyHopTable (void)
    {
        return m_listFrequencyHopTable.begin();
    }

     /** @brief  Returns the last element of the FrequencyHopTable sub-parameter list*/  
    inline std::list<CFrequencyHopTable *>::iterator
    endFrequencyHopTable (void)
    {
        return m_listFrequencyHopTable.end();
    }

     /** @brief  Clears the LLRP FrequencyHopTable sub-parameter list*/  
    inline void
    clearFrequencyHopTable (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listFrequencyHopTable);
    }

     /** @brief  Count of the LLRP FrequencyHopTable sub-parameter list*/  
    inline int
    countFrequencyHopTable (void)
    {
        return (int) (m_listFrequencyHopTable.size());
    }

    EResultCode
     /** @brief  Add a FrequencyHopTable to the LLRP sub-parameter list*/  
    addFrequencyHopTable (
      CFrequencyHopTable * pValue);


  
  
  protected:
    CFixedFrequencyTable * m_pFixedFrequencyTable;

  public:
    /** @brief Get accessor functions for the LLRP FixedFrequencyTable sub-parameter */  
    inline CFixedFrequencyTable *
    getFixedFrequencyTable (void)
    {
        return m_pFixedFrequencyTable;
    }

    /** @brief Set accessor functions for the LLRP FixedFrequencyTable sub-parameter */  
    EResultCode
    setFixedFrequencyTable (
      CFixedFrequencyTable * pValue);


};


/**
 ** @brief  Class Definition CFrequencyHopTable for LLRP parameter FrequencyHopTable
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=50&view=fit>LLRP Specification Section 9.2.4.1.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=134&view=fit>LLRP Specification Section 16.2.3.4.1.2.1</a>
  </li>
  
</ul>  

      
         
    <p>This parameter carries the frequency hop table parameters. This is used for Readers operating in regions with frequency hopping regulatory requirements. If the Reader is capable of storing multiple hop tables, the Reader may send all of them to the Client.</p> 
 
           
    <ul>
              
    <li>
    <p>HopTableID which is the index of the frequency hop table returned by the Reader.</p> 
 </li>
 
              
    <li>
    <p>This is followed by a list of the frequencies (in kKHhz) in hop table order. The one-based position of a frequency in the list is defined as its ChannelIndex (i.e. the first frequency is referred to as ChannelIndex one).</p> 
 </li>
 
            </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CFrequencyHopTable : public CParameter
{
  public:
    CFrequencyHopTable (void);
    ~CFrequencyHopTable (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u8_t m_HopTableID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHopTableID;
//@}

    /** @brief Get accessor functions for the LLRP HopTableID field */
    inline llrp_u8_t
    getHopTableID (void)
    {
        return m_HopTableID;
    }

    /** @brief Set accessor functions for the LLRP HopTableID field */
    inline void
    setHopTableID (
      llrp_u8_t value)
    {
        m_HopTableID = value;
    }


  
  
  
  protected:
    llrp_u32v_t m_Frequency;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdFrequency;
//@}

    /** @brief Get accessor functions for the LLRP Frequency field */
    inline llrp_u32v_t
    getFrequency (void)
    {
        return m_Frequency;
    }

    /** @brief Set accessor functions for the LLRP Frequency field */
    inline void
    setFrequency (
      llrp_u32v_t value)
    {
        m_Frequency = value;
    }


  
};


/**
 ** @brief  Class Definition CFixedFrequencyTable for LLRP parameter FixedFrequencyTable
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=50&view=fit>LLRP Specification Section 9.2.4.1.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=135&view=fit>LLRP Specification Section 16.2.3.4.1.2.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the fixed frequency list that can be used by the Reader. The one-based position of a frequency in the list is defined as its ChannelIndex (i.e. the first frequency is referred to as ChannelIndex one).</p> 
   
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CFixedFrequencyTable : public CParameter
{
  public:
    CFixedFrequencyTable (void);
    ~CFixedFrequencyTable (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32v_t m_Frequency;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdFrequency;
//@}

    /** @brief Get accessor functions for the LLRP Frequency field */
    inline llrp_u32v_t
    getFrequency (void)
    {
        return m_Frequency;
    }

    /** @brief Set accessor functions for the LLRP Frequency field */
    inline void
    setFrequency (
      llrp_u32v_t value)
    {
        m_Frequency = value;
    }


  
};


/**
 ** @brief  Class Definition CROSpec for LLRP parameter ROSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=55&view=fit>LLRP Specification Section 10.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=135&view=fit>LLRP Specification Section 16.2.4.1</a>
  </li>
  
</ul>  

   
    
    <p>This parameter carries the information of the Reader inventory and survey operation.</p> 
 
   <SMALL><i>Copyright 2006, 2007, EPCglobal Inc.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CROSpec : public CParameter
{
  public:
    CROSpec (void);
    ~CROSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
  
  
  protected:
    llrp_u8_t m_Priority;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPriority;
//@}

    /** @brief Get accessor functions for the LLRP Priority field */
    inline llrp_u8_t
    getPriority (void)
    {
        return m_Priority;
    }

    /** @brief Set accessor functions for the LLRP Priority field */
    inline void
    setPriority (
      llrp_u8_t value)
    {
        m_Priority = value;
    }


  
  
  
  protected:
    EROSpecState m_eCurrentState;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCurrentState;
//@}

    /** @brief Get accessor functions for the LLRP CurrentState field */
    inline EROSpecState
    getCurrentState (void)
    {
        return m_eCurrentState;
    }

    /** @brief Set accessor functions for the LLRP CurrentState field */
    inline void
    setCurrentState (
      EROSpecState value)
    {
        m_eCurrentState = value;
    }


  
  
  
  protected:
    CROBoundarySpec * m_pROBoundarySpec;

  public:
    /** @brief Get accessor functions for the LLRP ROBoundarySpec sub-parameter */  
    inline CROBoundarySpec *
    getROBoundarySpec (void)
    {
        return m_pROBoundarySpec;
    }

    /** @brief Set accessor functions for the LLRP ROBoundarySpec sub-parameter */  
    EResultCode
    setROBoundarySpec (
      CROBoundarySpec * pValue);


  
  
  protected:
    std::list<CParameter *> m_listSpecParameter;

  public:
     /** @brief  Returns the first element of the SpecParameter sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginSpecParameter (void)
    {
        return m_listSpecParameter.begin();
    }

     /** @brief  Returns the last element of the SpecParameter sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endSpecParameter (void)
    {
        return m_listSpecParameter.end();
    }

     /** @brief  Clears the LLRP SpecParameter sub-parameter list*/  
    inline void
    clearSpecParameter (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listSpecParameter);
    }

     /** @brief  Count of the LLRP SpecParameter sub-parameter list*/  
    inline int
    countSpecParameter (void)
    {
        return (int) (m_listSpecParameter.size());
    }

    EResultCode
     /** @brief  Add a SpecParameter to the LLRP sub-parameter list*/  
    addSpecParameter (
      CParameter * pValue);


  
  
  protected:
    CROReportSpec * m_pROReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP ROReportSpec sub-parameter */  
    inline CROReportSpec *
    getROReportSpec (void)
    {
        return m_pROReportSpec;
    }

    /** @brief Set accessor functions for the LLRP ROReportSpec sub-parameter */  
    EResultCode
    setROReportSpec (
      CROReportSpec * pValue);


};


/**
 ** @brief  Class Definition CROBoundarySpec for LLRP parameter ROBoundarySpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=55&view=fit>LLRP Specification Section 10.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=135&view=fit>LLRP Specification Section 16.2.4.1.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the lifetime of the command, ROStartTrigger and ROStopTrigger parameters.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CROBoundarySpec : public CParameter
{
  public:
    CROBoundarySpec (void);
    ~CROBoundarySpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CROSpecStartTrigger * m_pROSpecStartTrigger;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecStartTrigger sub-parameter */  
    inline CROSpecStartTrigger *
    getROSpecStartTrigger (void)
    {
        return m_pROSpecStartTrigger;
    }

    /** @brief Set accessor functions for the LLRP ROSpecStartTrigger sub-parameter */  
    EResultCode
    setROSpecStartTrigger (
      CROSpecStartTrigger * pValue);


  
  
  protected:
    CROSpecStopTrigger * m_pROSpecStopTrigger;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecStopTrigger sub-parameter */  
    inline CROSpecStopTrigger *
    getROSpecStopTrigger (void)
    {
        return m_pROSpecStopTrigger;
    }

    /** @brief Set accessor functions for the LLRP ROSpecStopTrigger sub-parameter */  
    EResultCode
    setROSpecStopTrigger (
      CROSpecStopTrigger * pValue);


};


/**
 ** @brief  Class Definition CROSpecStartTrigger for LLRP parameter ROSpecStartTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=56&view=fit>LLRP Specification Section 10.2.1.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=136&view=fit>LLRP Specification Section 16.2.4.1.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Describes the condition upon which the ROSpec will start execution.</p> 
 
       
  <HR>

    
    
    
    
  
 **/

  
  
  
class CROSpecStartTrigger : public CParameter
{
  public:
    CROSpecStartTrigger (void);
    ~CROSpecStartTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EROSpecStartTriggerType m_eROSpecStartTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecStartTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecStartTriggerType field */
    inline EROSpecStartTriggerType
    getROSpecStartTriggerType (void)
    {
        return m_eROSpecStartTriggerType;
    }

    /** @brief Set accessor functions for the LLRP ROSpecStartTriggerType field */
    inline void
    setROSpecStartTriggerType (
      EROSpecStartTriggerType value)
    {
        m_eROSpecStartTriggerType = value;
    }


  
  
  
  protected:
    CPeriodicTriggerValue * m_pPeriodicTriggerValue;

  public:
    /** @brief Get accessor functions for the LLRP PeriodicTriggerValue sub-parameter */  
    inline CPeriodicTriggerValue *
    getPeriodicTriggerValue (void)
    {
        return m_pPeriodicTriggerValue;
    }

    /** @brief Set accessor functions for the LLRP PeriodicTriggerValue sub-parameter */  
    EResultCode
    setPeriodicTriggerValue (
      CPeriodicTriggerValue * pValue);


  
  
  protected:
    CGPITriggerValue * m_pGPITriggerValue;

  public:
    /** @brief Get accessor functions for the LLRP GPITriggerValue sub-parameter */  
    inline CGPITriggerValue *
    getGPITriggerValue (void)
    {
        return m_pGPITriggerValue;
    }

    /** @brief Set accessor functions for the LLRP GPITriggerValue sub-parameter */  
    EResultCode
    setGPITriggerValue (
      CGPITriggerValue * pValue);


};


/**
 ** @brief  Class Definition CPeriodicTriggerValue for LLRP parameter PeriodicTriggerValue
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=56&view=fit>LLRP Specification Section 10.2.1.1.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=136&view=fit>LLRP Specification Section 16.2.4.1.1.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Periodic trigger is specified using UTC time, offset and period.</p> 
 
          
    <p>For one-shot inventory, period is set to 0, and for periodic inventory operation period > 0.</p> 
 
          
    <p>If UTC time is not specified, the first start time is determined as (time of message receipt + offset), else, the first start time is determined as (UTC time + offset). Subsequent start times  = first start time + k * period (where, k > 0).</p> 
 
          
    <p>If the Reader does not support UTC clock (as indicated by HasUTCClockCapability), and it receives the UTC time as part of the PeriodicTriggerValue parameter from the Client, the Reader 
   <b>SHALL</b>
  return an error.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CPeriodicTriggerValue : public CParameter
{
  public:
    CPeriodicTriggerValue (void);
    ~CPeriodicTriggerValue (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_Offset;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOffset;
//@}

    /** @brief Get accessor functions for the LLRP Offset field */
    inline llrp_u32_t
    getOffset (void)
    {
        return m_Offset;
    }

    /** @brief Set accessor functions for the LLRP Offset field */
    inline void
    setOffset (
      llrp_u32_t value)
    {
        m_Offset = value;
    }


  
  
  
  protected:
    llrp_u32_t m_Period;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPeriod;
//@}

    /** @brief Get accessor functions for the LLRP Period field */
    inline llrp_u32_t
    getPeriod (void)
    {
        return m_Period;
    }

    /** @brief Set accessor functions for the LLRP Period field */
    inline void
    setPeriod (
      llrp_u32_t value)
    {
        m_Period = value;
    }


  
  
  
  protected:
    CUTCTimestamp * m_pUTCTimestamp;

  public:
    /** @brief Get accessor functions for the LLRP UTCTimestamp sub-parameter */  
    inline CUTCTimestamp *
    getUTCTimestamp (void)
    {
        return m_pUTCTimestamp;
    }

    /** @brief Set accessor functions for the LLRP UTCTimestamp sub-parameter */  
    EResultCode
    setUTCTimestamp (
      CUTCTimestamp * pValue);


};


/**
 ** @brief  Class Definition CGPITriggerValue for LLRP parameter GPITriggerValue
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=57&view=fit>LLRP Specification Section 10.2.1.1.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=136&view=fit>LLRP Specification Section 16.2.4.1.1.1.2</a>
  </li>
  
</ul>  

      
          
    <p>This trigger is tied to an event on the General Purpose Input (GPI) of the Reader. The event is represented as a boolean type, and it is up to the internal implementation of the Reader to map exact physical event to a boolean type. For example, a 0 to 1 and a 1 to 0 transition on an input pin of the Reader could be mapped to a boolean true and a  boolean false event respectively.</p> 
  
          
    <p>This trigger parameter has a timeout value field. The timeout is useful for specifying a fail-safe timeout when this trigger is used as a stop trigger. When the timeout is 0, it indicates that there is no timeout. When used as a start trigger, the timeout value 
   <b>SHALL</b>
  be ignored.</p> 
 
          
    <p>Readers that do not support GPIs 
   <b>SHALL</b>
  return zero for numGPIs in the capabilities discovery. If the Client sets up the GPI trigger for such a Reader, the Reader 
   <b>SHALL</b>
  send an error message for the ADD_ROSPEC message and not add the ROSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CGPITriggerValue : public CParameter
{
  public:
    CGPITriggerValue (void);
    ~CGPITriggerValue (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_GPIPortNum;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIPortNum;
//@}

    /** @brief Get accessor functions for the LLRP GPIPortNum field */
    inline llrp_u16_t
    getGPIPortNum (void)
    {
        return m_GPIPortNum;
    }

    /** @brief Set accessor functions for the LLRP GPIPortNum field */
    inline void
    setGPIPortNum (
      llrp_u16_t value)
    {
        m_GPIPortNum = value;
    }


  
  
  
  protected:
    llrp_u1_t m_GPIEvent;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIEvent;
//@}

    /** @brief Get accessor functions for the LLRP GPIEvent field */
    inline llrp_u1_t
    getGPIEvent (void)
    {
        return m_GPIEvent;
    }

    /** @brief Set accessor functions for the LLRP GPIEvent field */
    inline void
    setGPIEvent (
      llrp_u1_t value)
    {
        m_GPIEvent = value;
    }


  
  
  
  protected:
    llrp_u32_t m_Timeout;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTimeout;
//@}

    /** @brief Get accessor functions for the LLRP Timeout field */
    inline llrp_u32_t
    getTimeout (void)
    {
        return m_Timeout;
    }

    /** @brief Set accessor functions for the LLRP Timeout field */
    inline void
    setTimeout (
      llrp_u32_t value)
    {
        m_Timeout = value;
    }


  
};


/**
 ** @brief  Class Definition CROSpecStopTrigger for LLRP parameter ROSpecStopTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=57&view=fit>LLRP Specification Section 10.2.1.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=136&view=fit>LLRP Specification Section 16.2.4.1.1.2</a>
  </li>
  
</ul>  

      
          
    <p>Describes the condition upon which the ROSpec will stop.</p> 
 
       
  <HR>

    
    
    
    
  
 **/

  
  
  
class CROSpecStopTrigger : public CParameter
{
  public:
    CROSpecStopTrigger (void);
    ~CROSpecStopTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EROSpecStopTriggerType m_eROSpecStopTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecStopTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecStopTriggerType field */
    inline EROSpecStopTriggerType
    getROSpecStopTriggerType (void)
    {
        return m_eROSpecStopTriggerType;
    }

    /** @brief Set accessor functions for the LLRP ROSpecStopTriggerType field */
    inline void
    setROSpecStopTriggerType (
      EROSpecStopTriggerType value)
    {
        m_eROSpecStopTriggerType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_DurationTriggerValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDurationTriggerValue;
//@}

    /** @brief Get accessor functions for the LLRP DurationTriggerValue field */
    inline llrp_u32_t
    getDurationTriggerValue (void)
    {
        return m_DurationTriggerValue;
    }

    /** @brief Set accessor functions for the LLRP DurationTriggerValue field */
    inline void
    setDurationTriggerValue (
      llrp_u32_t value)
    {
        m_DurationTriggerValue = value;
    }


  
  
  
  protected:
    CGPITriggerValue * m_pGPITriggerValue;

  public:
    /** @brief Get accessor functions for the LLRP GPITriggerValue sub-parameter */  
    inline CGPITriggerValue *
    getGPITriggerValue (void)
    {
        return m_pGPITriggerValue;
    }

    /** @brief Set accessor functions for the LLRP GPITriggerValue sub-parameter */  
    EResultCode
    setGPITriggerValue (
      CGPITriggerValue * pValue);


};


/**
 ** @brief  Class Definition CAISpec for LLRP parameter AISpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=57&view=fit>LLRP Specification Section 10.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=137&view=fit>LLRP Specification Section 16.2.4.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines antenna inventory operations.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CAISpec : public CParameter
{
  public:
    CAISpec (void);
    ~CAISpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16v_t m_AntennaIDs;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaIDs;
//@}

    /** @brief Get accessor functions for the LLRP AntennaIDs field */
    inline llrp_u16v_t
    getAntennaIDs (void)
    {
        return m_AntennaIDs;
    }

    /** @brief Set accessor functions for the LLRP AntennaIDs field */
    inline void
    setAntennaIDs (
      llrp_u16v_t value)
    {
        m_AntennaIDs = value;
    }


  
  
  
  protected:
    CAISpecStopTrigger * m_pAISpecStopTrigger;

  public:
    /** @brief Get accessor functions for the LLRP AISpecStopTrigger sub-parameter */  
    inline CAISpecStopTrigger *
    getAISpecStopTrigger (void)
    {
        return m_pAISpecStopTrigger;
    }

    /** @brief Set accessor functions for the LLRP AISpecStopTrigger sub-parameter */  
    EResultCode
    setAISpecStopTrigger (
      CAISpecStopTrigger * pValue);


  
  
  protected:
    std::list<CInventoryParameterSpec *> m_listInventoryParameterSpec;

  public:
     /** @brief  Returns the first element of the InventoryParameterSpec sub-parameter list*/  
    inline std::list<CInventoryParameterSpec *>::iterator
    beginInventoryParameterSpec (void)
    {
        return m_listInventoryParameterSpec.begin();
    }

     /** @brief  Returns the last element of the InventoryParameterSpec sub-parameter list*/  
    inline std::list<CInventoryParameterSpec *>::iterator
    endInventoryParameterSpec (void)
    {
        return m_listInventoryParameterSpec.end();
    }

     /** @brief  Clears the LLRP InventoryParameterSpec sub-parameter list*/  
    inline void
    clearInventoryParameterSpec (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listInventoryParameterSpec);
    }

     /** @brief  Count of the LLRP InventoryParameterSpec sub-parameter list*/  
    inline int
    countInventoryParameterSpec (void)
    {
        return (int) (m_listInventoryParameterSpec.size());
    }

    EResultCode
     /** @brief  Add a InventoryParameterSpec to the LLRP sub-parameter list*/  
    addInventoryParameterSpec (
      CInventoryParameterSpec * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CAISpecStopTrigger for LLRP parameter AISpecStopTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=58&view=fit>LLRP Specification Section 10.2.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=137&view=fit>LLRP Specification Section 16.2.4.2.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines the stop (i.e., terminating boundary) of an antenna inventory operation.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CAISpecStopTrigger : public CParameter
{
  public:
    CAISpecStopTrigger (void);
    ~CAISpecStopTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EAISpecStopTriggerType m_eAISpecStopTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAISpecStopTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP AISpecStopTriggerType field */
    inline EAISpecStopTriggerType
    getAISpecStopTriggerType (void)
    {
        return m_eAISpecStopTriggerType;
    }

    /** @brief Set accessor functions for the LLRP AISpecStopTriggerType field */
    inline void
    setAISpecStopTriggerType (
      EAISpecStopTriggerType value)
    {
        m_eAISpecStopTriggerType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_DurationTrigger;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDurationTrigger;
//@}

    /** @brief Get accessor functions for the LLRP DurationTrigger field */
    inline llrp_u32_t
    getDurationTrigger (void)
    {
        return m_DurationTrigger;
    }

    /** @brief Set accessor functions for the LLRP DurationTrigger field */
    inline void
    setDurationTrigger (
      llrp_u32_t value)
    {
        m_DurationTrigger = value;
    }


  
  
  
  protected:
    CGPITriggerValue * m_pGPITriggerValue;

  public:
    /** @brief Get accessor functions for the LLRP GPITriggerValue sub-parameter */  
    inline CGPITriggerValue *
    getGPITriggerValue (void)
    {
        return m_pGPITriggerValue;
    }

    /** @brief Set accessor functions for the LLRP GPITriggerValue sub-parameter */  
    EResultCode
    setGPITriggerValue (
      CGPITriggerValue * pValue);


  
  
  protected:
    CTagObservationTrigger * m_pTagObservationTrigger;

  public:
    /** @brief Get accessor functions for the LLRP TagObservationTrigger sub-parameter */  
    inline CTagObservationTrigger *
    getTagObservationTrigger (void)
    {
        return m_pTagObservationTrigger;
    }

    /** @brief Set accessor functions for the LLRP TagObservationTrigger sub-parameter */  
    EResultCode
    setTagObservationTrigger (
      CTagObservationTrigger * pValue);


};


/**
 ** @brief  Class Definition CTagObservationTrigger for LLRP parameter TagObservationTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=58&view=fit>LLRP Specification Section 10.2.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=137&view=fit>LLRP Specification Section 16.2.4.2.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Describes the boundary (stop) condition that is based on tag observations.</p> 
 
       
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CTagObservationTrigger : public CParameter
{
  public:
    CTagObservationTrigger (void);
    ~CTagObservationTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    ETagObservationTriggerType m_eTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP TriggerType field */
    inline ETagObservationTriggerType
    getTriggerType (void)
    {
        return m_eTriggerType;
    }

    /** @brief Set accessor functions for the LLRP TriggerType field */
    inline void
    setTriggerType (
      ETagObservationTriggerType value)
    {
        m_eTriggerType = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumberOfTags;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumberOfTags;
//@}

    /** @brief Get accessor functions for the LLRP NumberOfTags field */
    inline llrp_u16_t
    getNumberOfTags (void)
    {
        return m_NumberOfTags;
    }

    /** @brief Set accessor functions for the LLRP NumberOfTags field */
    inline void
    setNumberOfTags (
      llrp_u16_t value)
    {
        m_NumberOfTags = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumberOfAttempts;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumberOfAttempts;
//@}

    /** @brief Get accessor functions for the LLRP NumberOfAttempts field */
    inline llrp_u16_t
    getNumberOfAttempts (void)
    {
        return m_NumberOfAttempts;
    }

    /** @brief Set accessor functions for the LLRP NumberOfAttempts field */
    inline void
    setNumberOfAttempts (
      llrp_u16_t value)
    {
        m_NumberOfAttempts = value;
    }


  
  
  
  protected:
    llrp_u16_t m_T;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdT;
//@}

    /** @brief Get accessor functions for the LLRP T field */
    inline llrp_u16_t
    getT (void)
    {
        return m_T;
    }

    /** @brief Set accessor functions for the LLRP T field */
    inline void
    setT (
      llrp_u16_t value)
    {
        m_T = value;
    }


  
  
  
  protected:
    llrp_u32_t m_Timeout;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTimeout;
//@}

    /** @brief Get accessor functions for the LLRP Timeout field */
    inline llrp_u32_t
    getTimeout (void)
    {
        return m_Timeout;
    }

    /** @brief Set accessor functions for the LLRP Timeout field */
    inline void
    setTimeout (
      llrp_u32_t value)
    {
        m_Timeout = value;
    }


  
};


/**
 ** @brief  Class Definition CInventoryParameterSpec for LLRP parameter InventoryParameterSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=59&view=fit>LLRP Specification Section 10.2.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=137&view=fit>LLRP Specification Section 16.2.4.2.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines the inventory operation to be performed at all antennas specified in the corresponding AISpec. This parameter is composed of an InventoryParameterSpecID, a ProtocolID, and zero or more optional antenna configuration parameters. Antenna configurations for antennas not indicated by the AntennaIDs within the AISpec are ignored by the reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CInventoryParameterSpec : public CParameter
{
  public:
    CInventoryParameterSpec (void);
    ~CInventoryParameterSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_InventoryParameterSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdInventoryParameterSpecID;
//@}

    /** @brief Get accessor functions for the LLRP InventoryParameterSpecID field */
    inline llrp_u16_t
    getInventoryParameterSpecID (void)
    {
        return m_InventoryParameterSpecID;
    }

    /** @brief Set accessor functions for the LLRP InventoryParameterSpecID field */
    inline void
    setInventoryParameterSpecID (
      llrp_u16_t value)
    {
        m_InventoryParameterSpecID = value;
    }


  
  
  
  protected:
    EAirProtocols m_eProtocolID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdProtocolID;
//@}

    /** @brief Get accessor functions for the LLRP ProtocolID field */
    inline EAirProtocols
    getProtocolID (void)
    {
        return m_eProtocolID;
    }

    /** @brief Set accessor functions for the LLRP ProtocolID field */
    inline void
    setProtocolID (
      EAirProtocols value)
    {
        m_eProtocolID = value;
    }


  
  
  
  protected:
    std::list<CAntennaConfiguration *> m_listAntennaConfiguration;

  public:
     /** @brief  Returns the first element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    beginAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.begin();
    }

     /** @brief  Returns the last element of the AntennaConfiguration sub-parameter list*/  
    inline std::list<CAntennaConfiguration *>::iterator
    endAntennaConfiguration (void)
    {
        return m_listAntennaConfiguration.end();
    }

     /** @brief  Clears the LLRP AntennaConfiguration sub-parameter list*/  
    inline void
    clearAntennaConfiguration (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAntennaConfiguration);
    }

     /** @brief  Count of the LLRP AntennaConfiguration sub-parameter list*/  
    inline int
    countAntennaConfiguration (void)
    {
        return (int) (m_listAntennaConfiguration.size());
    }

    EResultCode
     /** @brief  Add a AntennaConfiguration to the LLRP sub-parameter list*/  
    addAntennaConfiguration (
      CAntennaConfiguration * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CRFSurveySpec for LLRP parameter RFSurveySpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=59&view=fit>LLRP Specification Section 10.2.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=138&view=fit>LLRP Specification Section 16.2.4.3</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines RF Survey operations. RF Survey is an operation during which the Reader performs a scan and measures the power levels across a set of frequencies at an antenna. This parameter defines the identifier of the antenna where this survey is to be performed, the duration of the survey operation (specified via stop trigger), and the range of frequencies to measure power levels of.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

  
  
  
class CRFSurveySpec : public CParameter
{
  public:
    CRFSurveySpec (void);
    ~CRFSurveySpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_StartFrequency;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdStartFrequency;
//@}

    /** @brief Get accessor functions for the LLRP StartFrequency field */
    inline llrp_u32_t
    getStartFrequency (void)
    {
        return m_StartFrequency;
    }

    /** @brief Set accessor functions for the LLRP StartFrequency field */
    inline void
    setStartFrequency (
      llrp_u32_t value)
    {
        m_StartFrequency = value;
    }


  
  
  
  protected:
    llrp_u32_t m_EndFrequency;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEndFrequency;
//@}

    /** @brief Get accessor functions for the LLRP EndFrequency field */
    inline llrp_u32_t
    getEndFrequency (void)
    {
        return m_EndFrequency;
    }

    /** @brief Set accessor functions for the LLRP EndFrequency field */
    inline void
    setEndFrequency (
      llrp_u32_t value)
    {
        m_EndFrequency = value;
    }


  
  
  
  protected:
    CRFSurveySpecStopTrigger * m_pRFSurveySpecStopTrigger;

  public:
    /** @brief Get accessor functions for the LLRP RFSurveySpecStopTrigger sub-parameter */  
    inline CRFSurveySpecStopTrigger *
    getRFSurveySpecStopTrigger (void)
    {
        return m_pRFSurveySpecStopTrigger;
    }

    /** @brief Set accessor functions for the LLRP RFSurveySpecStopTrigger sub-parameter */  
    EResultCode
    setRFSurveySpecStopTrigger (
      CRFSurveySpecStopTrigger * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CRFSurveySpecStopTrigger for LLRP parameter RFSurveySpecStopTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=60&view=fit>LLRP Specification Section 10.2.3.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=138&view=fit>LLRP Specification Section 16.2.4.3.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines the stop trigger for RF Survey operations.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CRFSurveySpecStopTrigger : public CParameter
{
  public:
    CRFSurveySpecStopTrigger (void);
    ~CRFSurveySpecStopTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    ERFSurveySpecStopTriggerType m_eStopTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdStopTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP StopTriggerType field */
    inline ERFSurveySpecStopTriggerType
    getStopTriggerType (void)
    {
        return m_eStopTriggerType;
    }

    /** @brief Set accessor functions for the LLRP StopTriggerType field */
    inline void
    setStopTriggerType (
      ERFSurveySpecStopTriggerType value)
    {
        m_eStopTriggerType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_DurationPeriod;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDurationPeriod;
//@}

    /** @brief Get accessor functions for the LLRP DurationPeriod field */
    inline llrp_u32_t
    getDurationPeriod (void)
    {
        return m_DurationPeriod;
    }

    /** @brief Set accessor functions for the LLRP DurationPeriod field */
    inline void
    setDurationPeriod (
      llrp_u32_t value)
    {
        m_DurationPeriod = value;
    }


  
  
  
  protected:
    llrp_u32_t m_N;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdN;
//@}

    /** @brief Get accessor functions for the LLRP N field */
    inline llrp_u32_t
    getN (void)
    {
        return m_N;
    }

    /** @brief Set accessor functions for the LLRP N field */
    inline void
    setN (
      llrp_u32_t value)
    {
        m_N = value;
    }


  
};


/**
 ** @brief  Class Definition CAccessSpec for LLRP parameter AccessSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=64&view=fit>LLRP Specification Section 11.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=138&view=fit>LLRP Specification Section 16.2.5.1</a>
  </li>
  
</ul>  

   
    
    <p>This parameter carries information of the Reader access operation.</p> 
 
   <SMALL><i>Copyright 2006, 2007, EPCglobal Inc.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CAccessSpec : public CParameter
{
  public:
    CAccessSpec (void);
    ~CAccessSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_AccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecID field */
    inline llrp_u32_t
    getAccessSpecID (void)
    {
        return m_AccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID field */
    inline void
    setAccessSpecID (
      llrp_u32_t value)
    {
        m_AccessSpecID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    EAirProtocols m_eProtocolID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdProtocolID;
//@}

    /** @brief Get accessor functions for the LLRP ProtocolID field */
    inline EAirProtocols
    getProtocolID (void)
    {
        return m_eProtocolID;
    }

    /** @brief Set accessor functions for the LLRP ProtocolID field */
    inline void
    setProtocolID (
      EAirProtocols value)
    {
        m_eProtocolID = value;
    }


  
  
  
  protected:
    EAccessSpecState m_eCurrentState;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCurrentState;
//@}

    /** @brief Get accessor functions for the LLRP CurrentState field */
    inline EAccessSpecState
    getCurrentState (void)
    {
        return m_eCurrentState;
    }

    /** @brief Set accessor functions for the LLRP CurrentState field */
    inline void
    setCurrentState (
      EAccessSpecState value)
    {
        m_eCurrentState = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
  
  
  protected:
    CAccessSpecStopTrigger * m_pAccessSpecStopTrigger;

  public:
    /** @brief Get accessor functions for the LLRP AccessSpecStopTrigger sub-parameter */  
    inline CAccessSpecStopTrigger *
    getAccessSpecStopTrigger (void)
    {
        return m_pAccessSpecStopTrigger;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecStopTrigger sub-parameter */  
    EResultCode
    setAccessSpecStopTrigger (
      CAccessSpecStopTrigger * pValue);


  
  
  protected:
    CAccessCommand * m_pAccessCommand;

  public:
    /** @brief Get accessor functions for the LLRP AccessCommand sub-parameter */  
    inline CAccessCommand *
    getAccessCommand (void)
    {
        return m_pAccessCommand;
    }

    /** @brief Set accessor functions for the LLRP AccessCommand sub-parameter */  
    EResultCode
    setAccessCommand (
      CAccessCommand * pValue);


  
  
  protected:
    CAccessReportSpec * m_pAccessReportSpec;

  public:
    /** @brief Get accessor functions for the LLRP AccessReportSpec sub-parameter */  
    inline CAccessReportSpec *
    getAccessReportSpec (void)
    {
        return m_pAccessReportSpec;
    }

    /** @brief Set accessor functions for the LLRP AccessReportSpec sub-parameter */  
    EResultCode
    setAccessReportSpec (
      CAccessReportSpec * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CAccessSpecStopTrigger for LLRP parameter AccessSpecStopTrigger
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=65&view=fit>LLRP Specification Section 11.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=139&view=fit>LLRP Specification Section 16.2.5.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Defines the condition upon which an AccessSpec will be automatically deleted</p> 
 
          
    <p>OperationCountValue:  A count to indicate the number of times this Spec is executed before it is deleted. If set to zero, this is equivalent to no stop trigger defined.</p> 
 
       
  <HR>

    
    
    
  
 **/

  
  
  
class CAccessSpecStopTrigger : public CParameter
{
  public:
    CAccessSpecStopTrigger (void);
    ~CAccessSpecStopTrigger (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EAccessSpecStopTriggerType m_eAccessSpecStopTrigger;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecStopTrigger;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecStopTrigger field */
    inline EAccessSpecStopTriggerType
    getAccessSpecStopTrigger (void)
    {
        return m_eAccessSpecStopTrigger;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecStopTrigger field */
    inline void
    setAccessSpecStopTrigger (
      EAccessSpecStopTriggerType value)
    {
        m_eAccessSpecStopTrigger = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OperationCountValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOperationCountValue;
//@}

    /** @brief Get accessor functions for the LLRP OperationCountValue field */
    inline llrp_u16_t
    getOperationCountValue (void)
    {
        return m_OperationCountValue;
    }

    /** @brief Set accessor functions for the LLRP OperationCountValue field */
    inline void
    setOperationCountValue (
      llrp_u16_t value)
    {
        m_OperationCountValue = value;
    }


  
};


/**
 ** @brief  Class Definition CAccessCommand for LLRP parameter AccessCommand
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=65&view=fit>LLRP Specification Section 11.2.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=139&view=fit>LLRP Specification Section 16.2.5.1.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines the air protocol access-specific settings. It contains a TagSpec and an OpSpec Parameter. The TagSpec specifies the tag filters in terms of air protocol specific memory capabilities (e.g., memory banks, pointer and length). The OpSpec specifies all the details of the operations required for the air protocol specific access operation commands.</p> 
 
          
    <p> In case there are multiple AccessSpecs that get matched during a TagSpec lookup, the Reader 
   <b>SHALL</b>
  only execute the first enabled AccessSpec that matches, where the ordering of the AccessSpecs is the order in which the AccessSpecs were created by the Client.</p> 
 
          
    <p>The order of execution of OpSpecs within an AccessSpec is the order in which the OpSpecs were set up in the AccessSpec. If an OpSpec execution fails, the Reader 
   <b>SHALL</b>
  stop the execution of the AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CAccessCommand : public CParameter
{
  public:
    CAccessCommand (void);
    ~CAccessCommand (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CParameter * m_pAirProtocolTagSpec;

  public:
    /** @brief Get accessor functions for the LLRP AirProtocolTagSpec sub-parameter */  
    inline CParameter *
    getAirProtocolTagSpec (void)
    {
        return m_pAirProtocolTagSpec;
    }

    /** @brief Set accessor functions for the LLRP AirProtocolTagSpec sub-parameter */  
    EResultCode
    setAirProtocolTagSpec (
      CParameter * pValue);


  
  
  protected:
    std::list<CParameter *> m_listAccessCommandOpSpec;

  public:
     /** @brief  Returns the first element of the AccessCommandOpSpec sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAccessCommandOpSpec (void)
    {
        return m_listAccessCommandOpSpec.begin();
    }

     /** @brief  Returns the last element of the AccessCommandOpSpec sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAccessCommandOpSpec (void)
    {
        return m_listAccessCommandOpSpec.end();
    }

     /** @brief  Clears the LLRP AccessCommandOpSpec sub-parameter list*/  
    inline void
    clearAccessCommandOpSpec (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAccessCommandOpSpec);
    }

     /** @brief  Count of the LLRP AccessCommandOpSpec sub-parameter list*/  
    inline int
    countAccessCommandOpSpec (void)
    {
        return (int) (m_listAccessCommandOpSpec.size());
    }

    EResultCode
     /** @brief  Add a AccessCommandOpSpec to the LLRP sub-parameter list*/  
    addAccessCommandOpSpec (
      CParameter * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CLLRPConfigurationStateValue for LLRP parameter LLRPConfigurationStateValue
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=71&view=fit>LLRP Specification Section 12.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=140&view=fit>LLRP Specification Section 16.2.6.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter, LLRPConfigurationStateValue, is a 32-bit value which represents a Reader's entire LLRP configuration state including: LLRP configuration parameters, vendor extension configuration parameters, ROSpecs, and AccessSpecs.  A Reader 
   <b>SHALL</b>
  change this value only:</p> 
 
          
    <ul>
              
    <li>
    <p>Upon successful execution of any of the following messages: ADD_ROSPEC, DELETE_ROSPEC, ADD_ACCESSSPEC, DELETE_ACCESSSPEC, SET_READER_CONFIG, or any CUSTOM_MESSAGE command that alters the reader's internal configuration.</p> 
  </li>
 
                 
    <li>
    <p>Upon an automatically deleted AccessSpec due to completion of OperationCountValue number of operations (Section 11.2.1.1).</p> 
 </li>
 
         </ul> 
 
         
    <p>A Reader 
   <b>SHALL</b>
  not change this value when the CurrentState of a ROSpec or AccessSpec changes.</p> 
 
          
    <p>The mechanism used to compute the LLRP configuration state value is implementation dependent.  However, a good implementation will insure that there's a high probability that the value will change when the Reader's configuration state changes.</p> 
  
          
    <p>It is expected that a Client will configure the Reader and then request the Reader's configuration state value.  The Client will then save this state value. If this value does not change between two requests for it, then a Client may assume that the above components of the LLRP configuration have also not changed.</p> 
 
          
    <p>When requested by a Client, the Reader 
   <b>SHALL</b>
  compute a state value based upon the Reader's current configuration state.  Upon each request, the Reader 
   <b>SHALL</b>
  return the same state value provided a Client has not altered the Reader's configuration state between requests.  Aside from this requirement, the computation of the state value is implementation dependent.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CLLRPConfigurationStateValue : public CParameter
{
  public:
    CLLRPConfigurationStateValue (void);
    ~CLLRPConfigurationStateValue (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_LLRPConfigurationStateValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdLLRPConfigurationStateValue;
//@}

    /** @brief Get accessor functions for the LLRP LLRPConfigurationStateValue field */
    inline llrp_u32_t
    getLLRPConfigurationStateValue (void)
    {
        return m_LLRPConfigurationStateValue;
    }

    /** @brief Set accessor functions for the LLRP LLRPConfigurationStateValue field */
    inline void
    setLLRPConfigurationStateValue (
      llrp_u32_t value)
    {
        m_LLRPConfigurationStateValue = value;
    }


  
};


/**
 ** @brief  Class Definition CIdentification for LLRP parameter Identification
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=72&view=fit>LLRP Specification Section 12.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=140&view=fit>LLRP Specification Section 16.2.6.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries an identification parameter that is unique within the local administration domain.  The identifier could be the Reader MAC address or EPC. The IDType defines the type of the identification value contained in this Parameter.</p> 
           
          
    <p>If IDType=0, the MAC address 
   <b>SHALL</b>
  be encoded as  EUI-64.[EUI64]</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CIdentification : public CParameter
{
  public:
    CIdentification (void);
    ~CIdentification (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EIdentificationType m_eIDType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdIDType;
//@}

    /** @brief Get accessor functions for the LLRP IDType field */
    inline EIdentificationType
    getIDType (void)
    {
        return m_eIDType;
    }

    /** @brief Set accessor functions for the LLRP IDType field */
    inline void
    setIDType (
      EIdentificationType value)
    {
        m_eIDType = value;
    }


  
  
  
  protected:
    llrp_u8v_t m_ReaderID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReaderID;
//@}

    /** @brief Get accessor functions for the LLRP ReaderID field */
    inline llrp_u8v_t
    getReaderID (void)
    {
        return m_ReaderID;
    }

    /** @brief Set accessor functions for the LLRP ReaderID field */
    inline void
    setReaderID (
      llrp_u8v_t value)
    {
        m_ReaderID = value;
    }


  
};


/**
 ** @brief  Class Definition CGPOWriteData for LLRP parameter GPOWriteData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=72&view=fit>LLRP Specification Section 12.2.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=140&view=fit>LLRP Specification Section 16.2.6.3</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the data pertinent to perform the write to a general purpose output port.</p> 
  
          
    <p>Readers that do not support GPOs 
   <b>SHALL</b>
  set NumGPOs in the GPIOCapabilities to zero. If such a Reader receives a SET_READER_CONFIG with GPOWriteData Parameter, the Reader 
   <b>SHALL</b>
  return an error message and not process any of the parameters in that message.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CGPOWriteData : public CParameter
{
  public:
    CGPOWriteData (void);
    ~CGPOWriteData (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_GPOPortNumber;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPOPortNumber;
//@}

    /** @brief Get accessor functions for the LLRP GPOPortNumber field */
    inline llrp_u16_t
    getGPOPortNumber (void)
    {
        return m_GPOPortNumber;
    }

    /** @brief Set accessor functions for the LLRP GPOPortNumber field */
    inline void
    setGPOPortNumber (
      llrp_u16_t value)
    {
        m_GPOPortNumber = value;
    }


  
  
  
  protected:
    llrp_u1_t m_GPOData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPOData;
//@}

    /** @brief Get accessor functions for the LLRP GPOData field */
    inline llrp_u1_t
    getGPOData (void)
    {
        return m_GPOData;
    }

    /** @brief Set accessor functions for the LLRP GPOData field */
    inline void
    setGPOData (
      llrp_u1_t value)
    {
        m_GPOData = value;
    }


  
};


/**
 ** @brief  Class Definition CKeepaliveSpec for LLRP parameter KeepaliveSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=73&view=fit>LLRP Specification Section 12.2.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=140&view=fit>LLRP Specification Section 16.2.6.4</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the specification for the keepalive message generation by the Reader. This includes the definition of the periodic trigger to send the keepalive message.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CKeepaliveSpec : public CParameter
{
  public:
    CKeepaliveSpec (void);
    ~CKeepaliveSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EKeepaliveTriggerType m_eKeepaliveTriggerType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdKeepaliveTriggerType;
//@}

    /** @brief Get accessor functions for the LLRP KeepaliveTriggerType field */
    inline EKeepaliveTriggerType
    getKeepaliveTriggerType (void)
    {
        return m_eKeepaliveTriggerType;
    }

    /** @brief Set accessor functions for the LLRP KeepaliveTriggerType field */
    inline void
    setKeepaliveTriggerType (
      EKeepaliveTriggerType value)
    {
        m_eKeepaliveTriggerType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_PeriodicTriggerValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPeriodicTriggerValue;
//@}

    /** @brief Get accessor functions for the LLRP PeriodicTriggerValue field */
    inline llrp_u32_t
    getPeriodicTriggerValue (void)
    {
        return m_PeriodicTriggerValue;
    }

    /** @brief Set accessor functions for the LLRP PeriodicTriggerValue field */
    inline void
    setPeriodicTriggerValue (
      llrp_u32_t value)
    {
        m_PeriodicTriggerValue = value;
    }


  
};


/**
 ** @brief  Class Definition CAntennaProperties for LLRP parameter AntennaProperties
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=73&view=fit>LLRP Specification Section 12.2.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=141&view=fit>LLRP Specification Section 16.2.6.5</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries a single antenna's properties. The properties include the gain and the connectivity status of the antenna.The antenna gain is the composite gain and includes the loss of the associated cable from the Reader to the antenna. The gain is represented in dBi*100 to allow fractional dBi representation.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CAntennaProperties : public CParameter
{
  public:
    CAntennaProperties (void);
    ~CAntennaProperties (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_AntennaConnected;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaConnected;
//@}

    /** @brief Get accessor functions for the LLRP AntennaConnected field */
    inline llrp_u1_t
    getAntennaConnected (void)
    {
        return m_AntennaConnected;
    }

    /** @brief Set accessor functions for the LLRP AntennaConnected field */
    inline void
    setAntennaConnected (
      llrp_u1_t value)
    {
        m_AntennaConnected = value;
    }


  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    llrp_s16_t m_AntennaGain;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaGain;
//@}

    /** @brief Get accessor functions for the LLRP AntennaGain field */
    inline llrp_s16_t
    getAntennaGain (void)
    {
        return m_AntennaGain;
    }

    /** @brief Set accessor functions for the LLRP AntennaGain field */
    inline void
    setAntennaGain (
      llrp_s16_t value)
    {
        m_AntennaGain = value;
    }


  
};


/**
 ** @brief  Class Definition CAntennaConfiguration for LLRP parameter AntennaConfiguration
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=74&view=fit>LLRP Specification Section 12.2.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=141&view=fit>LLRP Specification Section 16.2.6.6</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries a single antenna's configuration and it specifies the default values for the parameter set that are passed in this parameter block. The scope of the default values is the antenna. The default values are used for parameters during an operation on this antenna if the parameter was unspecified in the spec that describes the operation.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CAntennaConfiguration : public CParameter
{
  public:
    CAntennaConfiguration (void);
    ~CAntennaConfiguration (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
  
  
  protected:
    CRFReceiver * m_pRFReceiver;

  public:
    /** @brief Get accessor functions for the LLRP RFReceiver sub-parameter */  
    inline CRFReceiver *
    getRFReceiver (void)
    {
        return m_pRFReceiver;
    }

    /** @brief Set accessor functions for the LLRP RFReceiver sub-parameter */  
    EResultCode
    setRFReceiver (
      CRFReceiver * pValue);


  
  
  protected:
    CRFTransmitter * m_pRFTransmitter;

  public:
    /** @brief Get accessor functions for the LLRP RFTransmitter sub-parameter */  
    inline CRFTransmitter *
    getRFTransmitter (void)
    {
        return m_pRFTransmitter;
    }

    /** @brief Set accessor functions for the LLRP RFTransmitter sub-parameter */  
    EResultCode
    setRFTransmitter (
      CRFTransmitter * pValue);


  
  
  protected:
    std::list<CParameter *> m_listAirProtocolInventoryCommandSettings;

  public:
     /** @brief  Returns the first element of the AirProtocolInventoryCommandSettings sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAirProtocolInventoryCommandSettings (void)
    {
        return m_listAirProtocolInventoryCommandSettings.begin();
    }

     /** @brief  Returns the last element of the AirProtocolInventoryCommandSettings sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAirProtocolInventoryCommandSettings (void)
    {
        return m_listAirProtocolInventoryCommandSettings.end();
    }

     /** @brief  Clears the LLRP AirProtocolInventoryCommandSettings sub-parameter list*/  
    inline void
    clearAirProtocolInventoryCommandSettings (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAirProtocolInventoryCommandSettings);
    }

     /** @brief  Count of the LLRP AirProtocolInventoryCommandSettings sub-parameter list*/  
    inline int
    countAirProtocolInventoryCommandSettings (void)
    {
        return (int) (m_listAirProtocolInventoryCommandSettings.size());
    }

    EResultCode
     /** @brief  Add a AirProtocolInventoryCommandSettings to the LLRP sub-parameter list*/  
    addAirProtocolInventoryCommandSettings (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CRFReceiver for LLRP parameter RFReceiver
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=74&view=fit>LLRP Specification Section 12.2.6.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=141&view=fit>LLRP Specification Section 16.2.6.7</a>
  </li>
  
</ul>  

      
          
    <p>This Parameter carries the RF receiver information. The Receiver Sensitivity defines the sensitivity setting at the receiver. The value is the index into the ReceiveSensitivityTable (section 9.2.1.1).</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CRFReceiver : public CParameter
{
  public:
    CRFReceiver (void);
    ~CRFReceiver (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_ReceiverSensitivity;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReceiverSensitivity;
//@}

    /** @brief Get accessor functions for the LLRP ReceiverSensitivity field */
    inline llrp_u16_t
    getReceiverSensitivity (void)
    {
        return m_ReceiverSensitivity;
    }

    /** @brief Set accessor functions for the LLRP ReceiverSensitivity field */
    inline void
    setReceiverSensitivity (
      llrp_u16_t value)
    {
        m_ReceiverSensitivity = value;
    }


  
};


/**
 ** @brief  Class Definition CRFTransmitter for LLRP parameter RFTransmitter
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=74&view=fit>LLRP Specification Section 12.2.6.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=141&view=fit>LLRP Specification Section 16.2.6.8</a>
  </li>
  
</ul>  

      
          
    <p>This Parameter carries the RF transmitter information. The Transmit Power defines the transmit power for the antenna expressed as an index into the TransmitPowerTable (section 9.2.4.1.1). The HopTableID is the index of the frequency hop table to be used by the Reader (section 9.2.4.1.2.1) and is used when operating in frequency-hopping regulatory regions. This field is ignored in non-frequency-hopping regulatory regions. The ChannelIndex is the one-based channel index in the FixedFrequencyTable to use during transmission (section 9.2.4.1.2.2) and is used when operating in non-frequency-hopping regulatory regions. This field is ignored in frequency-hopping regulatory regions.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CRFTransmitter : public CParameter
{
  public:
    CRFTransmitter (void);
    ~CRFTransmitter (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_HopTableID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHopTableID;
//@}

    /** @brief Get accessor functions for the LLRP HopTableID field */
    inline llrp_u16_t
    getHopTableID (void)
    {
        return m_HopTableID;
    }

    /** @brief Set accessor functions for the LLRP HopTableID field */
    inline void
    setHopTableID (
      llrp_u16_t value)
    {
        m_HopTableID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_ChannelIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdChannelIndex;
//@}

    /** @brief Get accessor functions for the LLRP ChannelIndex field */
    inline llrp_u16_t
    getChannelIndex (void)
    {
        return m_ChannelIndex;
    }

    /** @brief Set accessor functions for the LLRP ChannelIndex field */
    inline void
    setChannelIndex (
      llrp_u16_t value)
    {
        m_ChannelIndex = value;
    }


  
  
  
  protected:
    llrp_u16_t m_TransmitPower;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTransmitPower;
//@}

    /** @brief Get accessor functions for the LLRP TransmitPower field */
    inline llrp_u16_t
    getTransmitPower (void)
    {
        return m_TransmitPower;
    }

    /** @brief Set accessor functions for the LLRP TransmitPower field */
    inline void
    setTransmitPower (
      llrp_u16_t value)
    {
        m_TransmitPower = value;
    }


  
};


/**
 ** @brief  Class Definition CGPIPortCurrentState for LLRP parameter GPIPortCurrentState
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=75&view=fit>LLRP Specification Section 12.2.6.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=142&view=fit>LLRP Specification Section 16.2.6.9</a>
  </li>
  
</ul>  

      
          
    <p>This Parameter carries the current configuration and state of a single GPI port.  In a SET_READER_CONFIG message, this parameter is used to enable or disable the GPI port using the GPIConfig field; the GPIState field is ignored by the reader.  In a GET_READER_CONFIG message, this parameter reports both the configuration and state of the GPI port.</p> 
 
          
    <p>When a ROSpec or AISpec is configured on a GPI-capable reader with GPI start and/or stop triggers, those GPIs must be enabled by the client with a SET_READER_CONFIG message for the triggers to function.</p> 
 
          
    <p>Readers that do not support GPIs 
   <b>SHALL</b>
  set NumGPIs in the GPIOCapabilities to zero. If such a Reader receives a GET_READER_CONFIG with a GPIPortCurrentState Parameter, the Reader 
   <b>SHALL</b>
  return an error message and not process any of the parameters in that message.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CGPIPortCurrentState : public CParameter
{
  public:
    CGPIPortCurrentState (void);
    ~CGPIPortCurrentState (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_GPIPortNum;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIPortNum;
//@}

    /** @brief Get accessor functions for the LLRP GPIPortNum field */
    inline llrp_u16_t
    getGPIPortNum (void)
    {
        return m_GPIPortNum;
    }

    /** @brief Set accessor functions for the LLRP GPIPortNum field */
    inline void
    setGPIPortNum (
      llrp_u16_t value)
    {
        m_GPIPortNum = value;
    }


  
  
  
  protected:
    llrp_u1_t m_Config;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdConfig;
//@}

    /** @brief Get accessor functions for the LLRP Config field */
    inline llrp_u1_t
    getConfig (void)
    {
        return m_Config;
    }

    /** @brief Set accessor functions for the LLRP Config field */
    inline void
    setConfig (
      llrp_u1_t value)
    {
        m_Config = value;
    }


  
  
  
  protected:
    EGPIPortState m_eState;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdState;
//@}

    /** @brief Get accessor functions for the LLRP State field */
    inline EGPIPortState
    getState (void)
    {
        return m_eState;
    }

    /** @brief Set accessor functions for the LLRP State field */
    inline void
    setState (
      EGPIPortState value)
    {
        m_eState = value;
    }


  
};


/**
 ** @brief  Class Definition CEventsAndReports for LLRP parameter EventsAndReports
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=75&view=fit>LLRP Specification Section 12.2.6.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=142&view=fit>LLRP Specification Section 16.2.6.10</a>
  </li>
  
</ul>  

      
          
    <p>This parameter controls the behavior of the Reader when a new LLRP connection is established. In a SET_READER_CONFIG message, this parameter is used to enable or disable the holding of events and reports upon connection using the HoldEventsAndReportsUponReconnect field. In a GET_READER_CONFIG message, this parameter reports the current configuration. If the HoldEventsAndReportsUponReconnect is true, the reader will not deliver any reports or events (except the ConnectionAttemptEvent) to the Client until the Client issues an ENABLE_EVENTS_AND_REPORTS message. Once the ENABLE_EVENTS_AND_REPORTS message is received the reader ceases its hold on events and reports for the duration of the connection.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CEventsAndReports : public CParameter
{
  public:
    CEventsAndReports (void);
    ~CEventsAndReports (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_HoldEventsAndReportsUponReconnect;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHoldEventsAndReportsUponReconnect;
//@}

    /** @brief Get accessor functions for the LLRP HoldEventsAndReportsUponReconnect field */
    inline llrp_u1_t
    getHoldEventsAndReportsUponReconnect (void)
    {
        return m_HoldEventsAndReportsUponReconnect;
    }

    /** @brief Set accessor functions for the LLRP HoldEventsAndReportsUponReconnect field */
    inline void
    setHoldEventsAndReportsUponReconnect (
      llrp_u1_t value)
    {
        m_HoldEventsAndReportsUponReconnect = value;
    }


  
};


/**
 ** @brief  Class Definition CROReportSpec for LLRP parameter ROReportSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=78&view=fit>LLRP Specification Section 13.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=142&view=fit>LLRP Specification Section 16.2.7.1</a>
  </li>
  
</ul>  

      
          
    <p>This Parameter carries the Reader inventory and RF survey reporting definition for the antenna. This parameter describes the contents of the report sent by the Reader and defines the events that cause the report to be sent.</p> 
 
          
    <p>The ROReportTrigger field defines the events that cause the report to be sent.</p> 
  
          
    <p>The TagReportContentSelector parameter defines the desired contents of the report. The ROReportTrigger defines the event that causes the report to be sent by the Reader to the Client.</p> 
 
          
    <p>See section 13.2.6.1 for details about the order that reports are to be sent with respect to Reader event notifications.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CROReportSpec : public CParameter
{
  public:
    CROReportSpec (void);
    ~CROReportSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EROReportTriggerType m_eROReportTrigger;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROReportTrigger;
//@}

    /** @brief Get accessor functions for the LLRP ROReportTrigger field */
    inline EROReportTriggerType
    getROReportTrigger (void)
    {
        return m_eROReportTrigger;
    }

    /** @brief Set accessor functions for the LLRP ROReportTrigger field */
    inline void
    setROReportTrigger (
      EROReportTriggerType value)
    {
        m_eROReportTrigger = value;
    }


  
  
  
  protected:
    llrp_u16_t m_N;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdN;
//@}

    /** @brief Get accessor functions for the LLRP N field */
    inline llrp_u16_t
    getN (void)
    {
        return m_N;
    }

    /** @brief Set accessor functions for the LLRP N field */
    inline void
    setN (
      llrp_u16_t value)
    {
        m_N = value;
    }


  
  
  
  protected:
    CTagReportContentSelector * m_pTagReportContentSelector;

  public:
    /** @brief Get accessor functions for the LLRP TagReportContentSelector sub-parameter */  
    inline CTagReportContentSelector *
    getTagReportContentSelector (void)
    {
        return m_pTagReportContentSelector;
    }

    /** @brief Set accessor functions for the LLRP TagReportContentSelector sub-parameter */  
    EResultCode
    setTagReportContentSelector (
      CTagReportContentSelector * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CTagReportContentSelector for LLRP parameter TagReportContentSelector
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=78&view=fit>LLRP Specification Section 13.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=142&view=fit>LLRP Specification Section 16.2.7.1.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used to configure the contents that are of interest in TagReportData. If enabled, the field is reported along with the tag data in the TagReportData.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CTagReportContentSelector : public CParameter
{
  public:
    CTagReportContentSelector (void);
    ~CTagReportContentSelector (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_EnableROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP EnableROSpecID field */
    inline llrp_u1_t
    getEnableROSpecID (void)
    {
        return m_EnableROSpecID;
    }

    /** @brief Set accessor functions for the LLRP EnableROSpecID field */
    inline void
    setEnableROSpecID (
      llrp_u1_t value)
    {
        m_EnableROSpecID = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableSpecIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableSpecIndex;
//@}

    /** @brief Get accessor functions for the LLRP EnableSpecIndex field */
    inline llrp_u1_t
    getEnableSpecIndex (void)
    {
        return m_EnableSpecIndex;
    }

    /** @brief Set accessor functions for the LLRP EnableSpecIndex field */
    inline void
    setEnableSpecIndex (
      llrp_u1_t value)
    {
        m_EnableSpecIndex = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableInventoryParameterSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableInventoryParameterSpecID;
//@}

    /** @brief Get accessor functions for the LLRP EnableInventoryParameterSpecID field */
    inline llrp_u1_t
    getEnableInventoryParameterSpecID (void)
    {
        return m_EnableInventoryParameterSpecID;
    }

    /** @brief Set accessor functions for the LLRP EnableInventoryParameterSpecID field */
    inline void
    setEnableInventoryParameterSpecID (
      llrp_u1_t value)
    {
        m_EnableInventoryParameterSpecID = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableAntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP EnableAntennaID field */
    inline llrp_u1_t
    getEnableAntennaID (void)
    {
        return m_EnableAntennaID;
    }

    /** @brief Set accessor functions for the LLRP EnableAntennaID field */
    inline void
    setEnableAntennaID (
      llrp_u1_t value)
    {
        m_EnableAntennaID = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableChannelIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableChannelIndex;
//@}

    /** @brief Get accessor functions for the LLRP EnableChannelIndex field */
    inline llrp_u1_t
    getEnableChannelIndex (void)
    {
        return m_EnableChannelIndex;
    }

    /** @brief Set accessor functions for the LLRP EnableChannelIndex field */
    inline void
    setEnableChannelIndex (
      llrp_u1_t value)
    {
        m_EnableChannelIndex = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnablePeakRSSI;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnablePeakRSSI;
//@}

    /** @brief Get accessor functions for the LLRP EnablePeakRSSI field */
    inline llrp_u1_t
    getEnablePeakRSSI (void)
    {
        return m_EnablePeakRSSI;
    }

    /** @brief Set accessor functions for the LLRP EnablePeakRSSI field */
    inline void
    setEnablePeakRSSI (
      llrp_u1_t value)
    {
        m_EnablePeakRSSI = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableFirstSeenTimestamp;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableFirstSeenTimestamp;
//@}

    /** @brief Get accessor functions for the LLRP EnableFirstSeenTimestamp field */
    inline llrp_u1_t
    getEnableFirstSeenTimestamp (void)
    {
        return m_EnableFirstSeenTimestamp;
    }

    /** @brief Set accessor functions for the LLRP EnableFirstSeenTimestamp field */
    inline void
    setEnableFirstSeenTimestamp (
      llrp_u1_t value)
    {
        m_EnableFirstSeenTimestamp = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableLastSeenTimestamp;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableLastSeenTimestamp;
//@}

    /** @brief Get accessor functions for the LLRP EnableLastSeenTimestamp field */
    inline llrp_u1_t
    getEnableLastSeenTimestamp (void)
    {
        return m_EnableLastSeenTimestamp;
    }

    /** @brief Set accessor functions for the LLRP EnableLastSeenTimestamp field */
    inline void
    setEnableLastSeenTimestamp (
      llrp_u1_t value)
    {
        m_EnableLastSeenTimestamp = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableTagSeenCount;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableTagSeenCount;
//@}

    /** @brief Get accessor functions for the LLRP EnableTagSeenCount field */
    inline llrp_u1_t
    getEnableTagSeenCount (void)
    {
        return m_EnableTagSeenCount;
    }

    /** @brief Set accessor functions for the LLRP EnableTagSeenCount field */
    inline void
    setEnableTagSeenCount (
      llrp_u1_t value)
    {
        m_EnableTagSeenCount = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnableAccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP EnableAccessSpecID field */
    inline llrp_u1_t
    getEnableAccessSpecID (void)
    {
        return m_EnableAccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP EnableAccessSpecID field */
    inline void
    setEnableAccessSpecID (
      llrp_u1_t value)
    {
        m_EnableAccessSpecID = value;
    }


  
  
  
  protected:
    std::list<CParameter *> m_listAirProtocolEPCMemorySelector;

  public:
     /** @brief  Returns the first element of the AirProtocolEPCMemorySelector sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAirProtocolEPCMemorySelector (void)
    {
        return m_listAirProtocolEPCMemorySelector.begin();
    }

     /** @brief  Returns the last element of the AirProtocolEPCMemorySelector sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAirProtocolEPCMemorySelector (void)
    {
        return m_listAirProtocolEPCMemorySelector.end();
    }

     /** @brief  Clears the LLRP AirProtocolEPCMemorySelector sub-parameter list*/  
    inline void
    clearAirProtocolEPCMemorySelector (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAirProtocolEPCMemorySelector);
    }

     /** @brief  Count of the LLRP AirProtocolEPCMemorySelector sub-parameter list*/  
    inline int
    countAirProtocolEPCMemorySelector (void)
    {
        return (int) (m_listAirProtocolEPCMemorySelector.size());
    }

    EResultCode
     /** @brief  Add a AirProtocolEPCMemorySelector to the LLRP sub-parameter list*/  
    addAirProtocolEPCMemorySelector (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CAccessReportSpec for LLRP parameter AccessReportSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=79&view=fit>LLRP Specification Section 13.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=143&view=fit>LLRP Specification Section 16.2.7.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter sets up the triggers for the Reader to send the access results to the Client. In addition, the Client can enable or disable reporting of ROSpec details in the access results.</p> 
   
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CAccessReportSpec : public CParameter
{
  public:
    CAccessReportSpec (void);
    ~CAccessReportSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EAccessReportTriggerType m_eAccessReportTrigger;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessReportTrigger;
//@}

    /** @brief Get accessor functions for the LLRP AccessReportTrigger field */
    inline EAccessReportTriggerType
    getAccessReportTrigger (void)
    {
        return m_eAccessReportTrigger;
    }

    /** @brief Set accessor functions for the LLRP AccessReportTrigger field */
    inline void
    setAccessReportTrigger (
      EAccessReportTriggerType value)
    {
        m_eAccessReportTrigger = value;
    }


  
};


/**
 ** @brief  Class Definition CTagReportData for LLRP parameter TagReportData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=80&view=fit>LLRP Specification Section 13.2.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=143&view=fit>LLRP Specification Section 16.2.7.3</a>
  </li>
  
</ul>  

      
          
    <p>This report parameter is generated per tag per accumulation scope. The only mandatory portion of this parameter is the EPCData parameter. If there was an access operation performed on the tag, the results of the OpSpecs are mandatory in the report. The other sub-parameters in this report are optional. LLRP provides three ways to make the tag reporting efficient:</p> 
 
          
             
    <li>
    <p>Allow parameters to be enabled or disabled via TagReportContentSelector (section 13.2.1.1) in TagReportSpec. </p> 
 </li>
 
             
    <li>
    <p>If an optional parameter is enabled, and is absent in the report, the Client 
   <b>SHALL</b>
  assume that the value is identical to the last parameter of the same type received. For example, this allows the Readers to not send a parameter in the report whose value has not changed since the last time it was sent by the Reader.</p> 
 </li>
 
             
    <li>
    <p>Allow accumulation of tag reports. See next section for details of accumulation.</p> 
 </li>
 
          
          
    <p>A Reader 
   <b>MAY</b>
  accumulate multiple tag reports into a single tag report.. If a Reader accumulates, the Reader 
   <b>SHALL</b>
  follow the accumulation rules specified in this section. The following specifies the rules for accumulating multiple tag observations into a single TagReportData:</p> 
 
          
    <ul>
            
    <li>
    <p>EPCData:</p> 
 </li>
 
              
    <ul>
    <li>
    <p>The Reader 
   <b>SHALL</b>
  not accumulate tag reports that do not have the same EPCData value.</p> 
 </li>
 </ul> 
 
            
    <li>
    <p>OpSpecResultList:</p> 
 </li>
  
                
    <ul>
    <li>
    <p>The Reader 
   <b>SHALL</b>
  not accumulate tag reports that do not have the same value for the OpSpec results in the OpSpecResultList.</p> 
 </li>
 </ul> 
 
            
    <li>
    <p>SpecID, SpecIndex, InventoryParameterSpecID, AntennaID, AirProtocolTagData, AccessSpecID:</p> 
 </li>
  
                
    <ul>
    <li>
    <p>These fields are optional, and their reporting can be enabled by the Client. If the Client has enabled one or more fields listed above, the Reader 
   <b>SHALL</b>
  not accumulate tag reports that do not have the same value for all the enabled fields.</p> 
 </li>
 </ul> 
 
            
    <li>
    <p>FirstSeenTimestamp, LastSeenTimestamp, PeakRSSI, TagSeenCount, ChannelIndex</p> 
 </li>
 
                
    <ul>
    <li>
    <p>These fields are optional, and their reporting can be enabled by the Client. If the field is enabled, the Reader sets the value of these fields as follows:</p> 
 </li>
 
                  
    <ul>
                      
    <li>
    <p>FirstSeenTimestamp: The Reader 
   <b>SHALL</b>
  set it to the time of the first observation amongst the tag reports that get accumulated in the TagReportData.</p> 
 </li>
 
                      
    <li>
    <p>LastSeenTimestamp: The Reader 
   <b>SHALL</b>
  set it to the time of the last observation amongst the tag reports that get accumulated in the TagReportData.</p> 
 </li>
 
                      
    <li>
    <p>PeakRSSI: The Reader 
   <b>SHALL</b>
  set it to the maximum RSSI value observed amongst the tag reports that get accumulated in the TagReportData.</p> 
 </li>
 
                      
    <li>
    <p>ChannelIndex: The Reader 
   <b>MAY</b>
  set it to the index of the first channel the tag was seen.</p> 
 </li>
 
                      
    <li>
    <p>TagSeenCount: The Reader 
   <b>SHALL</b>
  set it to the number of tag reports that get accumulated in the TagReportData.</p> 
 </li>
 
                  </ul> 
 
                 </ul> 
 
            </ul> 
     
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CTagReportData : public CParameter
{
  public:
    CTagReportData (void);
    ~CTagReportData (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CParameter * m_pEPCParameter;

  public:
    /** @brief Get accessor functions for the LLRP EPCParameter sub-parameter */  
    inline CParameter *
    getEPCParameter (void)
    {
        return m_pEPCParameter;
    }

    /** @brief Set accessor functions for the LLRP EPCParameter sub-parameter */  
    EResultCode
    setEPCParameter (
      CParameter * pValue);


  
  
  protected:
    CROSpecID * m_pROSpecID;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecID sub-parameter */  
    inline CROSpecID *
    getROSpecID (void)
    {
        return m_pROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID sub-parameter */  
    EResultCode
    setROSpecID (
      CROSpecID * pValue);


  
  
  protected:
    CSpecIndex * m_pSpecIndex;

  public:
    /** @brief Get accessor functions for the LLRP SpecIndex sub-parameter */  
    inline CSpecIndex *
    getSpecIndex (void)
    {
        return m_pSpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex sub-parameter */  
    EResultCode
    setSpecIndex (
      CSpecIndex * pValue);


  
  
  protected:
    CInventoryParameterSpecID * m_pInventoryParameterSpecID;

  public:
    /** @brief Get accessor functions for the LLRP InventoryParameterSpecID sub-parameter */  
    inline CInventoryParameterSpecID *
    getInventoryParameterSpecID (void)
    {
        return m_pInventoryParameterSpecID;
    }

    /** @brief Set accessor functions for the LLRP InventoryParameterSpecID sub-parameter */  
    EResultCode
    setInventoryParameterSpecID (
      CInventoryParameterSpecID * pValue);


  
  
  protected:
    CAntennaID * m_pAntennaID;

  public:
    /** @brief Get accessor functions for the LLRP AntennaID sub-parameter */  
    inline CAntennaID *
    getAntennaID (void)
    {
        return m_pAntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID sub-parameter */  
    EResultCode
    setAntennaID (
      CAntennaID * pValue);


  
  
  protected:
    CPeakRSSI * m_pPeakRSSI;

  public:
    /** @brief Get accessor functions for the LLRP PeakRSSI sub-parameter */  
    inline CPeakRSSI *
    getPeakRSSI (void)
    {
        return m_pPeakRSSI;
    }

    /** @brief Set accessor functions for the LLRP PeakRSSI sub-parameter */  
    EResultCode
    setPeakRSSI (
      CPeakRSSI * pValue);


  
  
  protected:
    CChannelIndex * m_pChannelIndex;

  public:
    /** @brief Get accessor functions for the LLRP ChannelIndex sub-parameter */  
    inline CChannelIndex *
    getChannelIndex (void)
    {
        return m_pChannelIndex;
    }

    /** @brief Set accessor functions for the LLRP ChannelIndex sub-parameter */  
    EResultCode
    setChannelIndex (
      CChannelIndex * pValue);


  
  
  protected:
    CFirstSeenTimestampUTC * m_pFirstSeenTimestampUTC;

  public:
    /** @brief Get accessor functions for the LLRP FirstSeenTimestampUTC sub-parameter */  
    inline CFirstSeenTimestampUTC *
    getFirstSeenTimestampUTC (void)
    {
        return m_pFirstSeenTimestampUTC;
    }

    /** @brief Set accessor functions for the LLRP FirstSeenTimestampUTC sub-parameter */  
    EResultCode
    setFirstSeenTimestampUTC (
      CFirstSeenTimestampUTC * pValue);


  
  
  protected:
    CFirstSeenTimestampUptime * m_pFirstSeenTimestampUptime;

  public:
    /** @brief Get accessor functions for the LLRP FirstSeenTimestampUptime sub-parameter */  
    inline CFirstSeenTimestampUptime *
    getFirstSeenTimestampUptime (void)
    {
        return m_pFirstSeenTimestampUptime;
    }

    /** @brief Set accessor functions for the LLRP FirstSeenTimestampUptime sub-parameter */  
    EResultCode
    setFirstSeenTimestampUptime (
      CFirstSeenTimestampUptime * pValue);


  
  
  protected:
    CLastSeenTimestampUTC * m_pLastSeenTimestampUTC;

  public:
    /** @brief Get accessor functions for the LLRP LastSeenTimestampUTC sub-parameter */  
    inline CLastSeenTimestampUTC *
    getLastSeenTimestampUTC (void)
    {
        return m_pLastSeenTimestampUTC;
    }

    /** @brief Set accessor functions for the LLRP LastSeenTimestampUTC sub-parameter */  
    EResultCode
    setLastSeenTimestampUTC (
      CLastSeenTimestampUTC * pValue);


  
  
  protected:
    CLastSeenTimestampUptime * m_pLastSeenTimestampUptime;

  public:
    /** @brief Get accessor functions for the LLRP LastSeenTimestampUptime sub-parameter */  
    inline CLastSeenTimestampUptime *
    getLastSeenTimestampUptime (void)
    {
        return m_pLastSeenTimestampUptime;
    }

    /** @brief Set accessor functions for the LLRP LastSeenTimestampUptime sub-parameter */  
    EResultCode
    setLastSeenTimestampUptime (
      CLastSeenTimestampUptime * pValue);


  
  
  protected:
    CTagSeenCount * m_pTagSeenCount;

  public:
    /** @brief Get accessor functions for the LLRP TagSeenCount sub-parameter */  
    inline CTagSeenCount *
    getTagSeenCount (void)
    {
        return m_pTagSeenCount;
    }

    /** @brief Set accessor functions for the LLRP TagSeenCount sub-parameter */  
    EResultCode
    setTagSeenCount (
      CTagSeenCount * pValue);


  
  
  protected:
    std::list<CParameter *> m_listAirProtocolTagData;

  public:
     /** @brief  Returns the first element of the AirProtocolTagData sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAirProtocolTagData (void)
    {
        return m_listAirProtocolTagData.begin();
    }

     /** @brief  Returns the last element of the AirProtocolTagData sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAirProtocolTagData (void)
    {
        return m_listAirProtocolTagData.end();
    }

     /** @brief  Clears the LLRP AirProtocolTagData sub-parameter list*/  
    inline void
    clearAirProtocolTagData (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAirProtocolTagData);
    }

     /** @brief  Count of the LLRP AirProtocolTagData sub-parameter list*/  
    inline int
    countAirProtocolTagData (void)
    {
        return (int) (m_listAirProtocolTagData.size());
    }

    EResultCode
     /** @brief  Add a AirProtocolTagData to the LLRP sub-parameter list*/  
    addAirProtocolTagData (
      CParameter * pValue);


  
  
  protected:
    CAccessSpecID * m_pAccessSpecID;

  public:
    /** @brief Get accessor functions for the LLRP AccessSpecID sub-parameter */  
    inline CAccessSpecID *
    getAccessSpecID (void)
    {
        return m_pAccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID sub-parameter */  
    EResultCode
    setAccessSpecID (
      CAccessSpecID * pValue);


  
  
  protected:
    std::list<CParameter *> m_listAccessCommandOpSpecResult;

  public:
     /** @brief  Returns the first element of the AccessCommandOpSpecResult sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginAccessCommandOpSpecResult (void)
    {
        return m_listAccessCommandOpSpecResult.begin();
    }

     /** @brief  Returns the last element of the AccessCommandOpSpecResult sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endAccessCommandOpSpecResult (void)
    {
        return m_listAccessCommandOpSpecResult.end();
    }

     /** @brief  Clears the LLRP AccessCommandOpSpecResult sub-parameter list*/  
    inline void
    clearAccessCommandOpSpecResult (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listAccessCommandOpSpecResult);
    }

     /** @brief  Count of the LLRP AccessCommandOpSpecResult sub-parameter list*/  
    inline int
    countAccessCommandOpSpecResult (void)
    {
        return (int) (m_listAccessCommandOpSpecResult.size());
    }

    EResultCode
     /** @brief  Add a AccessCommandOpSpecResult to the LLRP sub-parameter list*/  
    addAccessCommandOpSpecResult (
      CParameter * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CEPCData for LLRP parameter EPCData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=82&view=fit>LLRP Specification Section 13.2.3.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=144&view=fit>LLRP Specification Section 16.2.7.3.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the EPC identifier information.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CEPCData : public CParameter
{
  public:
    CEPCData (void);
    ~CEPCData (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1v_t m_EPC;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEPC;
//@}

    /** @brief Get accessor functions for the LLRP EPC field */
    inline llrp_u1v_t
    getEPC (void)
    {
        return m_EPC;
    }

    /** @brief Set accessor functions for the LLRP EPC field */
    inline void
    setEPC (
      llrp_u1v_t value)
    {
        m_EPC = value;
    }


  
};


/**
 ** @brief  Class Definition CEPC_96 for LLRP parameter EPC_96
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=82&view=fit>LLRP Specification Section 13.2.3.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=144&view=fit>LLRP Specification Section 16.2.7.3.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries 96-bit EPC identifier information.</p> 
 
       
  <HR>

    
    
  
 **/

  
  
  
class CEPC_96 : public CParameter
{
  public:
    CEPC_96 (void);
    ~CEPC_96 (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u96_t m_EPC;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEPC;
//@}

    /** @brief Get accessor functions for the LLRP EPC field */
    inline llrp_u96_t
    getEPC (void)
    {
        return m_EPC;
    }

    /** @brief Set accessor functions for the LLRP EPC field */
    inline void
    setEPC (
      llrp_u96_t value)
    {
        m_EPC = value;
    }


  
};


/**
 ** @brief  Class Definition CROSpecID for LLRP parameter ROSpecID
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=82&view=fit>LLRP Specification Section 13.2.3.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=144&view=fit>LLRP Specification Section 16.2.7.3.3</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the ROSpecID information.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CROSpecID : public CParameter
{
  public:
    CROSpecID (void);
    ~CROSpecID (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CSpecIndex for LLRP parameter SpecIndex
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=82&view=fit>LLRP Specification Section 13.2.3.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.4</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the SpecIndex information. The SpecIndex indicates the item within the ROSpec that was being executed at the time the tag was observed.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CSpecIndex : public CParameter
{
  public:
    CSpecIndex (void);
    ~CSpecIndex (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_SpecIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSpecIndex;
//@}

    /** @brief Get accessor functions for the LLRP SpecIndex field */
    inline llrp_u16_t
    getSpecIndex (void)
    {
        return m_SpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex field */
    inline void
    setSpecIndex (
      llrp_u16_t value)
    {
        m_SpecIndex = value;
    }


  
};


/**
 ** @brief  Class Definition CInventoryParameterSpecID for LLRP parameter InventoryParameterSpecID
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=83&view=fit>LLRP Specification Section 13.2.3.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.5</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the InventoryParameterSpecID information.</p> 
           
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CInventoryParameterSpecID : public CParameter
{
  public:
    CInventoryParameterSpecID (void);
    ~CInventoryParameterSpecID (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_InventoryParameterSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdInventoryParameterSpecID;
//@}

    /** @brief Get accessor functions for the LLRP InventoryParameterSpecID field */
    inline llrp_u16_t
    getInventoryParameterSpecID (void)
    {
        return m_InventoryParameterSpecID;
    }

    /** @brief Set accessor functions for the LLRP InventoryParameterSpecID field */
    inline void
    setInventoryParameterSpecID (
      llrp_u16_t value)
    {
        m_InventoryParameterSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CAntennaID for LLRP parameter AntennaID
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=83&view=fit>LLRP Specification Section 13.2.3.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.6</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the AntennaID information.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CAntennaID : public CParameter
{
  public:
    CAntennaID (void);
    ~CAntennaID (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
};


/**
 ** @brief  Class Definition CPeakRSSI for LLRP parameter PeakRSSI
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=83&view=fit>LLRP Specification Section 13.2.3.7</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.7</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the PeakRSSI information.</p> 
 
          
    <p>PeakRSSI: The peak received power of the EPC backscatter in dBm.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CPeakRSSI : public CParameter
{
  public:
    CPeakRSSI (void);
    ~CPeakRSSI (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_s8_t m_PeakRSSI;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPeakRSSI;
//@}

    /** @brief Get accessor functions for the LLRP PeakRSSI field */
    inline llrp_s8_t
    getPeakRSSI (void)
    {
        return m_PeakRSSI;
    }

    /** @brief Set accessor functions for the LLRP PeakRSSI field */
    inline void
    setPeakRSSI (
      llrp_s8_t value)
    {
        m_PeakRSSI = value;
    }


  
};


/**
 ** @brief  Class Definition CChannelIndex for LLRP parameter ChannelIndex
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=83&view=fit>LLRP Specification Section 13.2.3.8</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.8</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the one-based ChannelIndex informationvalue.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CChannelIndex : public CParameter
{
  public:
    CChannelIndex (void);
    ~CChannelIndex (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_ChannelIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdChannelIndex;
//@}

    /** @brief Get accessor functions for the LLRP ChannelIndex field */
    inline llrp_u16_t
    getChannelIndex (void)
    {
        return m_ChannelIndex;
    }

    /** @brief Set accessor functions for the LLRP ChannelIndex field */
    inline void
    setChannelIndex (
      llrp_u16_t value)
    {
        m_ChannelIndex = value;
    }


  
};


/**
 ** @brief  Class Definition CFirstSeenTimestampUTC for LLRP parameter FirstSeenTimestampUTC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=83&view=fit>LLRP Specification Section 13.2.3.9</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.9</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the FirstSeenTimestamp information in UTC.</p> 
 
          
    <p>Compliant Readers and Clients that have UTC clocks 
   <b>SHALL</b>
  implement this parameter.</p> 
 
          
    <p>This is the time elapsed since the Epoch (00:00:00 UTC, January 1, 1970) measured in microseconds.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CFirstSeenTimestampUTC : public CParameter
{
  public:
    CFirstSeenTimestampUTC (void);
    ~CFirstSeenTimestampUTC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CFirstSeenTimestampUptime for LLRP parameter FirstSeenTimestampUptime
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=84&view=fit>LLRP Specification Section 13.2.3.10</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=145&view=fit>LLRP Specification Section 16.2.7.3.10</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the FirstSeenTimestamp information in Uptime.</p> 
           
          
    <p>Compliant Readers and Clients that do not have UTC clocks 
   <b>SHALL</b>
  implement this parameter. Compliant Readers and Clients that have UTC clocks 
   <b>MAY</b>
  implement this parameter.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CFirstSeenTimestampUptime : public CParameter
{
  public:
    CFirstSeenTimestampUptime (void);
    ~CFirstSeenTimestampUptime (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CLastSeenTimestampUTC for LLRP parameter LastSeenTimestampUTC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=84&view=fit>LLRP Specification Section 13.2.3.11</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=146&view=fit>LLRP Specification Section 16.2.7.3.11</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the LastSeenTimestamp information in UTC.</p> 
 
          
    <p>This is the time elapsed since boot, measured in microseconds.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CLastSeenTimestampUTC : public CParameter
{
  public:
    CLastSeenTimestampUTC (void);
    ~CLastSeenTimestampUTC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CLastSeenTimestampUptime for LLRP parameter LastSeenTimestampUptime
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=84&view=fit>LLRP Specification Section 13.2.3.12</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=146&view=fit>LLRP Specification Section 16.2.7.3.12</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the LastSeenTimestamp information in UTC.</p> 
 
          
    <p>This is the time elapsed since the Epoch (00:00:00 UTC, January 1, 1970) measured in microseconds.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CLastSeenTimestampUptime : public CParameter
{
  public:
    CLastSeenTimestampUptime (void);
    ~CLastSeenTimestampUptime (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u64_t m_Microseconds;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMicroseconds;
//@}

    /** @brief Get accessor functions for the LLRP Microseconds field */
    inline llrp_u64_t
    getMicroseconds (void)
    {
        return m_Microseconds;
    }

    /** @brief Set accessor functions for the LLRP Microseconds field */
    inline void
    setMicroseconds (
      llrp_u64_t value)
    {
        m_Microseconds = value;
    }


  
};


/**
 ** @brief  Class Definition CTagSeenCount for LLRP parameter TagSeenCount
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=84&view=fit>LLRP Specification Section 13.2.3.13</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=146&view=fit>LLRP Specification Section 16.2.7.3.13</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the tag seen count information. If TagSeenCount > 65535 for the report period, the reader 
   <b>SHALL</b>
  report 65535.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CTagSeenCount : public CParameter
{
  public:
    CTagSeenCount (void);
    ~CTagSeenCount (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_TagCount;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagCount;
//@}

    /** @brief Get accessor functions for the LLRP TagCount field */
    inline llrp_u16_t
    getTagCount (void)
    {
        return m_TagCount;
    }

    /** @brief Set accessor functions for the LLRP TagCount field */
    inline void
    setTagCount (
      llrp_u16_t value)
    {
        m_TagCount = value;
    }


  
};


/**
 ** @brief  Class Definition CAccessSpecID for LLRP parameter AccessSpecID
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=85&view=fit>LLRP Specification Section 13.2.3.15</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=146&view=fit>LLRP Specification Section 16.2.7.3.15</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the AccessSpecID information.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CAccessSpecID : public CParameter
{
  public:
    CAccessSpecID (void);
    ~CAccessSpecID (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_AccessSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessSpecID;
//@}

    /** @brief Get accessor functions for the LLRP AccessSpecID field */
    inline llrp_u32_t
    getAccessSpecID (void)
    {
        return m_AccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID field */
    inline void
    setAccessSpecID (
      llrp_u32_t value)
    {
        m_AccessSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CRFSurveyReportData for LLRP parameter RFSurveyReportData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=85&view=fit>LLRP Specification Section 13.2.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=147&view=fit>LLRP Specification Section 16.2.7.4</a>
  </li>
  
</ul>  

      
          
    <p>This describes the content of the RF Survey Report.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CRFSurveyReportData : public CParameter
{
  public:
    CRFSurveyReportData (void);
    ~CRFSurveyReportData (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CROSpecID * m_pROSpecID;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecID sub-parameter */  
    inline CROSpecID *
    getROSpecID (void)
    {
        return m_pROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID sub-parameter */  
    EResultCode
    setROSpecID (
      CROSpecID * pValue);


  
  
  protected:
    CSpecIndex * m_pSpecIndex;

  public:
    /** @brief Get accessor functions for the LLRP SpecIndex sub-parameter */  
    inline CSpecIndex *
    getSpecIndex (void)
    {
        return m_pSpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex sub-parameter */  
    EResultCode
    setSpecIndex (
      CSpecIndex * pValue);


  
  
  protected:
    std::list<CFrequencyRSSILevelEntry *> m_listFrequencyRSSILevelEntry;

  public:
     /** @brief  Returns the first element of the FrequencyRSSILevelEntry sub-parameter list*/  
    inline std::list<CFrequencyRSSILevelEntry *>::iterator
    beginFrequencyRSSILevelEntry (void)
    {
        return m_listFrequencyRSSILevelEntry.begin();
    }

     /** @brief  Returns the last element of the FrequencyRSSILevelEntry sub-parameter list*/  
    inline std::list<CFrequencyRSSILevelEntry *>::iterator
    endFrequencyRSSILevelEntry (void)
    {
        return m_listFrequencyRSSILevelEntry.end();
    }

     /** @brief  Clears the LLRP FrequencyRSSILevelEntry sub-parameter list*/  
    inline void
    clearFrequencyRSSILevelEntry (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listFrequencyRSSILevelEntry);
    }

     /** @brief  Count of the LLRP FrequencyRSSILevelEntry sub-parameter list*/  
    inline int
    countFrequencyRSSILevelEntry (void)
    {
        return (int) (m_listFrequencyRSSILevelEntry.size());
    }

    EResultCode
     /** @brief  Add a FrequencyRSSILevelEntry to the LLRP sub-parameter list*/  
    addFrequencyRSSILevelEntry (
      CFrequencyRSSILevelEntry * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CFrequencyRSSILevelEntry for LLRP parameter FrequencyRSSILevelEntry
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=85&view=fit>LLRP Specification Section 13.2.4.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=147&view=fit>LLRP Specification Section 16.2.7.4.1</a>
  </li>
  
</ul>  

      
        
    <p>Description</p> 
 
        
    <ul>
            
    <li>
    <p>Frequency:  The frequency on which the measurement was taken, specified in kHz.</p> 
 </li>
 
            
    <li>
    <p>Bandwidth:  The measurement bandwidth of the measurement in kHz.</p> 
 </li>
 
            
    <li>
    <p>Average RSSI: The average power level observed at this frequency in dBm.</p> 
 </li>
 
            
    <li>
    <p>Peak RSSI: The peak power level observed at this frequency in dBm.</p> 
 </li>
 
          </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

  
  
  
class CFrequencyRSSILevelEntry : public CParameter
{
  public:
    CFrequencyRSSILevelEntry (void);
    ~CFrequencyRSSILevelEntry (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_Frequency;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdFrequency;
//@}

    /** @brief Get accessor functions for the LLRP Frequency field */
    inline llrp_u32_t
    getFrequency (void)
    {
        return m_Frequency;
    }

    /** @brief Set accessor functions for the LLRP Frequency field */
    inline void
    setFrequency (
      llrp_u32_t value)
    {
        m_Frequency = value;
    }


  
  
  
  protected:
    llrp_u32_t m_Bandwidth;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdBandwidth;
//@}

    /** @brief Get accessor functions for the LLRP Bandwidth field */
    inline llrp_u32_t
    getBandwidth (void)
    {
        return m_Bandwidth;
    }

    /** @brief Set accessor functions for the LLRP Bandwidth field */
    inline void
    setBandwidth (
      llrp_u32_t value)
    {
        m_Bandwidth = value;
    }


  
  
  
  protected:
    llrp_s8_t m_AverageRSSI;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAverageRSSI;
//@}

    /** @brief Get accessor functions for the LLRP AverageRSSI field */
    inline llrp_s8_t
    getAverageRSSI (void)
    {
        return m_AverageRSSI;
    }

    /** @brief Set accessor functions for the LLRP AverageRSSI field */
    inline void
    setAverageRSSI (
      llrp_s8_t value)
    {
        m_AverageRSSI = value;
    }


  
  
  
  protected:
    llrp_s8_t m_PeakRSSI;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPeakRSSI;
//@}

    /** @brief Get accessor functions for the LLRP PeakRSSI field */
    inline llrp_s8_t
    getPeakRSSI (void)
    {
        return m_PeakRSSI;
    }

    /** @brief Set accessor functions for the LLRP PeakRSSI field */
    inline void
    setPeakRSSI (
      llrp_s8_t value)
    {
        m_PeakRSSI = value;
    }


  
  
  
  protected:
    CParameter * m_pTimestamp;

  public:
    /** @brief Get accessor functions for the LLRP Timestamp sub-parameter */  
    inline CParameter *
    getTimestamp (void)
    {
        return m_pTimestamp;
    }

    /** @brief Set accessor functions for the LLRP Timestamp sub-parameter */  
    EResultCode
    setTimestamp (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CReaderEventNotificationSpec for LLRP parameter ReaderEventNotificationSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=86&view=fit>LLRP Specification Section 13.2.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=147&view=fit>LLRP Specification Section 16.2.7.5</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used by the Client to enable or disable notification of one or more Reader events. Notification of buffer overflow events and connection events (attempt/close) are mandatory, and not configurable.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CReaderEventNotificationSpec : public CParameter
{
  public:
    CReaderEventNotificationSpec (void);
    ~CReaderEventNotificationSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    std::list<CEventNotificationState *> m_listEventNotificationState;

  public:
     /** @brief  Returns the first element of the EventNotificationState sub-parameter list*/  
    inline std::list<CEventNotificationState *>::iterator
    beginEventNotificationState (void)
    {
        return m_listEventNotificationState.begin();
    }

     /** @brief  Returns the last element of the EventNotificationState sub-parameter list*/  
    inline std::list<CEventNotificationState *>::iterator
    endEventNotificationState (void)
    {
        return m_listEventNotificationState.end();
    }

     /** @brief  Clears the LLRP EventNotificationState sub-parameter list*/  
    inline void
    clearEventNotificationState (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listEventNotificationState);
    }

     /** @brief  Count of the LLRP EventNotificationState sub-parameter list*/  
    inline int
    countEventNotificationState (void)
    {
        return (int) (m_listEventNotificationState.size());
    }

    EResultCode
     /** @brief  Add a EventNotificationState to the LLRP sub-parameter list*/  
    addEventNotificationState (
      CEventNotificationState * pValue);


};


/**
 ** @brief  Class Definition CEventNotificationState for LLRP parameter EventNotificationState
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=86&view=fit>LLRP Specification Section 13.2.5.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=148&view=fit>LLRP Specification Section 16.2.7.5.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used to enable or disable notification of a single Reader event type.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CEventNotificationState : public CParameter
{
  public:
    CEventNotificationState (void);
    ~CEventNotificationState (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    ENotificationEventType m_eEventType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEventType;
//@}

    /** @brief Get accessor functions for the LLRP EventType field */
    inline ENotificationEventType
    getEventType (void)
    {
        return m_eEventType;
    }

    /** @brief Set accessor functions for the LLRP EventType field */
    inline void
    setEventType (
      ENotificationEventType value)
    {
        m_eEventType = value;
    }


  
  
  
  protected:
    llrp_u1_t m_NotificationState;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNotificationState;
//@}

    /** @brief Get accessor functions for the LLRP NotificationState field */
    inline llrp_u1_t
    getNotificationState (void)
    {
        return m_NotificationState;
    }

    /** @brief Set accessor functions for the LLRP NotificationState field */
    inline void
    setNotificationState (
      llrp_u1_t value)
    {
        m_NotificationState = value;
    }


  
};


/**
 ** @brief  Class Definition CReaderEventNotificationData for LLRP parameter ReaderEventNotificationData
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=86&view=fit>LLRP Specification Section 13.2.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=148&view=fit>LLRP Specification Section 16.2.7.6</a>
  </li>
  
</ul>  

      
          
    <p>This parameter describes the contents of the event notification sent by the Reader, and defines the events that cause the notification to be sent. Event notification messages may be sent by the Reader due to connection establishment/closing event, critical events such as hopping, fault-detection in a Reader functional block, buffer overflow, due to the activation of a Reader accessory trigger input (e.g. motion detection), or due to performance monitoring events such as abnormalities in the RF environment.</p> 
  
          
    <p>Timestamp is the time that the events reported occurred.</p> 
 
          
    <p>LLRP assumes a reliable stream transport mechanism.  Messages sent through LLRP will arrive in the order that they were sent over the transport and binding utilized. Status events within the same message 
   <b>SHALL</b>
  be ordered chronologically.</p> 
 
          
    <p>Status events delivered by reader event notifications are useful, especially in conjunction with the tag report data.  The following describes the requirements of the reader event notifications ordering with respect to the ordering of tag reports and Reader Event Notifications.  </p> 
 
          
    <p>The following requirements are made on the ordering of Event Parameters with respect to each other and to tag report Parameters.  These statements apply if the respective status events and report triggers are enabled. </p> 
 
          
    <ul>
            
    <li>
    <p>If the start of an ROSpec is triggered by a GPI, the GPIEvent Parameter 
   <b>SHALL</b>
  be sent before the ROSpecEvent Parameter signaling the start of the ROSpec.</p> 
 </li>
 
            
    <li>
    <p>If the end of an ROSpec is triggered by a GPI, the GPIEvent Parameter 
   <b>SHALL</b>
  be sent before the ROSpecEvent Parameter signaling the end of the ROSpec.</p> 
 </li>
 
            
    <li>
    <p>If an ROSpec contains one or more AISpecs, the ROSpecEvent parameter signaling the end of an ROSpec 
   <b>SHALL</b>
  be sent after the AISpecEvent Parameter signaling the end of the last AISpec within that ROSpec.</p> 
 </li>
 
            
    <li>
    <p>If one ROSpec pre-empts another ROSpec, the ROSpecEvent parameter signaling the preemption of the first ROSpec 
   <b>SHALL</b>
  be sent before the ROSpecEvent parameter signaling the start of the next ROSpec.</p> 
 </li>
 
            
    <li>
    <p>Tag data received during an ROSpec execution 
   <b>SHALL</b>
  be sent between the ROSpecEvent parameter signaling the start of the ROSpec and the ROSpecEvent parameter signaling the end or preemption of the ROSpec if the ROReportTrigger is not set to "None".</p> 
 </li>
 
            
    <li>
    <p>Tag data received during an AISpec execution 
   <b>SHALL</b>
  be sent before the AISpecEvent Parameter signaling the end of the AISpec if the ROReportTrigger is not "None" or "end of RO Spec"</p> 
 </li>
 
            
    <li>
    <p>Tag data received during the time on a channel 
   <b>SHALL</b>
  be sent after the HoppingEvent parameter that announced this channel and before the next HoppingEvent parameter when the ROReportTrigger is not "None" and N=1.</p> 
 </li>
 
          </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CReaderEventNotificationData : public CParameter
{
  public:
    CReaderEventNotificationData (void);
    ~CReaderEventNotificationData (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    CParameter * m_pTimestamp;

  public:
    /** @brief Get accessor functions for the LLRP Timestamp sub-parameter */  
    inline CParameter *
    getTimestamp (void)
    {
        return m_pTimestamp;
    }

    /** @brief Set accessor functions for the LLRP Timestamp sub-parameter */  
    EResultCode
    setTimestamp (
      CParameter * pValue);


  
  
  protected:
    CHoppingEvent * m_pHoppingEvent;

  public:
    /** @brief Get accessor functions for the LLRP HoppingEvent sub-parameter */  
    inline CHoppingEvent *
    getHoppingEvent (void)
    {
        return m_pHoppingEvent;
    }

    /** @brief Set accessor functions for the LLRP HoppingEvent sub-parameter */  
    EResultCode
    setHoppingEvent (
      CHoppingEvent * pValue);


  
  
  protected:
    CGPIEvent * m_pGPIEvent;

  public:
    /** @brief Get accessor functions for the LLRP GPIEvent sub-parameter */  
    inline CGPIEvent *
    getGPIEvent (void)
    {
        return m_pGPIEvent;
    }

    /** @brief Set accessor functions for the LLRP GPIEvent sub-parameter */  
    EResultCode
    setGPIEvent (
      CGPIEvent * pValue);


  
  
  protected:
    CROSpecEvent * m_pROSpecEvent;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecEvent sub-parameter */  
    inline CROSpecEvent *
    getROSpecEvent (void)
    {
        return m_pROSpecEvent;
    }

    /** @brief Set accessor functions for the LLRP ROSpecEvent sub-parameter */  
    EResultCode
    setROSpecEvent (
      CROSpecEvent * pValue);


  
  
  protected:
    CReportBufferLevelWarningEvent * m_pReportBufferLevelWarningEvent;

  public:
    /** @brief Get accessor functions for the LLRP ReportBufferLevelWarningEvent sub-parameter */  
    inline CReportBufferLevelWarningEvent *
    getReportBufferLevelWarningEvent (void)
    {
        return m_pReportBufferLevelWarningEvent;
    }

    /** @brief Set accessor functions for the LLRP ReportBufferLevelWarningEvent sub-parameter */  
    EResultCode
    setReportBufferLevelWarningEvent (
      CReportBufferLevelWarningEvent * pValue);


  
  
  protected:
    CReportBufferOverflowErrorEvent * m_pReportBufferOverflowErrorEvent;

  public:
    /** @brief Get accessor functions for the LLRP ReportBufferOverflowErrorEvent sub-parameter */  
    inline CReportBufferOverflowErrorEvent *
    getReportBufferOverflowErrorEvent (void)
    {
        return m_pReportBufferOverflowErrorEvent;
    }

    /** @brief Set accessor functions for the LLRP ReportBufferOverflowErrorEvent sub-parameter */  
    EResultCode
    setReportBufferOverflowErrorEvent (
      CReportBufferOverflowErrorEvent * pValue);


  
  
  protected:
    CReaderExceptionEvent * m_pReaderExceptionEvent;

  public:
    /** @brief Get accessor functions for the LLRP ReaderExceptionEvent sub-parameter */  
    inline CReaderExceptionEvent *
    getReaderExceptionEvent (void)
    {
        return m_pReaderExceptionEvent;
    }

    /** @brief Set accessor functions for the LLRP ReaderExceptionEvent sub-parameter */  
    EResultCode
    setReaderExceptionEvent (
      CReaderExceptionEvent * pValue);


  
  
  protected:
    CRFSurveyEvent * m_pRFSurveyEvent;

  public:
    /** @brief Get accessor functions for the LLRP RFSurveyEvent sub-parameter */  
    inline CRFSurveyEvent *
    getRFSurveyEvent (void)
    {
        return m_pRFSurveyEvent;
    }

    /** @brief Set accessor functions for the LLRP RFSurveyEvent sub-parameter */  
    EResultCode
    setRFSurveyEvent (
      CRFSurveyEvent * pValue);


  
  
  protected:
    CAISpecEvent * m_pAISpecEvent;

  public:
    /** @brief Get accessor functions for the LLRP AISpecEvent sub-parameter */  
    inline CAISpecEvent *
    getAISpecEvent (void)
    {
        return m_pAISpecEvent;
    }

    /** @brief Set accessor functions for the LLRP AISpecEvent sub-parameter */  
    EResultCode
    setAISpecEvent (
      CAISpecEvent * pValue);


  
  
  protected:
    CAntennaEvent * m_pAntennaEvent;

  public:
    /** @brief Get accessor functions for the LLRP AntennaEvent sub-parameter */  
    inline CAntennaEvent *
    getAntennaEvent (void)
    {
        return m_pAntennaEvent;
    }

    /** @brief Set accessor functions for the LLRP AntennaEvent sub-parameter */  
    EResultCode
    setAntennaEvent (
      CAntennaEvent * pValue);


  
  
  protected:
    CConnectionAttemptEvent * m_pConnectionAttemptEvent;

  public:
    /** @brief Get accessor functions for the LLRP ConnectionAttemptEvent sub-parameter */  
    inline CConnectionAttemptEvent *
    getConnectionAttemptEvent (void)
    {
        return m_pConnectionAttemptEvent;
    }

    /** @brief Set accessor functions for the LLRP ConnectionAttemptEvent sub-parameter */  
    EResultCode
    setConnectionAttemptEvent (
      CConnectionAttemptEvent * pValue);


  
  
  protected:
    CConnectionCloseEvent * m_pConnectionCloseEvent;

  public:
    /** @brief Get accessor functions for the LLRP ConnectionCloseEvent sub-parameter */  
    inline CConnectionCloseEvent *
    getConnectionCloseEvent (void)
    {
        return m_pConnectionCloseEvent;
    }

    /** @brief Set accessor functions for the LLRP ConnectionCloseEvent sub-parameter */  
    EResultCode
    setConnectionCloseEvent (
      CConnectionCloseEvent * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CHoppingEvent for LLRP parameter HoppingEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=88&view=fit>LLRP Specification Section 13.2.6.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=148&view=fit>LLRP Specification Section 16.2.7.6.1</a>
  </li>
  
</ul>  

      
          
    <p>A Reader reports this event every time it hops frequency.</p> 
 
          
    <p>NextChannelIndex: This is the one-based ChannelIindex of the next channel to which the Reader is going to hop change to. The channel Ids are listed in the Frequency Hop Table.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CHoppingEvent : public CParameter
{
  public:
    CHoppingEvent (void);
    ~CHoppingEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_HopTableID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdHopTableID;
//@}

    /** @brief Get accessor functions for the LLRP HopTableID field */
    inline llrp_u16_t
    getHopTableID (void)
    {
        return m_HopTableID;
    }

    /** @brief Set accessor functions for the LLRP HopTableID field */
    inline void
    setHopTableID (
      llrp_u16_t value)
    {
        m_HopTableID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NextChannelIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNextChannelIndex;
//@}

    /** @brief Get accessor functions for the LLRP NextChannelIndex field */
    inline llrp_u16_t
    getNextChannelIndex (void)
    {
        return m_NextChannelIndex;
    }

    /** @brief Set accessor functions for the LLRP NextChannelIndex field */
    inline void
    setNextChannelIndex (
      llrp_u16_t value)
    {
        m_NextChannelIndex = value;
    }


  
};


/**
 ** @brief  Class Definition CGPIEvent for LLRP parameter GPIEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=88&view=fit>LLRP Specification Section 13.2.6.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=149&view=fit>LLRP Specification Section 16.2.7.6.2</a>
  </li>
  
</ul>  

      
          
    <p>A reader reports this event every time an enabled GPI changes GPIstate.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CGPIEvent : public CParameter
{
  public:
    CGPIEvent (void);
    ~CGPIEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_GPIPortNumber;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIPortNumber;
//@}

    /** @brief Get accessor functions for the LLRP GPIPortNumber field */
    inline llrp_u16_t
    getGPIPortNumber (void)
    {
        return m_GPIPortNumber;
    }

    /** @brief Set accessor functions for the LLRP GPIPortNumber field */
    inline void
    setGPIPortNumber (
      llrp_u16_t value)
    {
        m_GPIPortNumber = value;
    }


  
  
  
  protected:
    llrp_u1_t m_GPIEvent;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdGPIEvent;
//@}

    /** @brief Get accessor functions for the LLRP GPIEvent field */
    inline llrp_u1_t
    getGPIEvent (void)
    {
        return m_GPIEvent;
    }

    /** @brief Set accessor functions for the LLRP GPIEvent field */
    inline void
    setGPIEvent (
      llrp_u1_t value)
    {
        m_GPIEvent = value;
    }


  
};


/**
 ** @brief  Class Definition CROSpecEvent for LLRP parameter ROSpecEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=89&view=fit>LLRP Specification Section 13.2.6.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=149&view=fit>LLRP Specification Section 16.2.7.6.3</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the ROSpec event details. The EventType could be start or end of the ROSpec.</p> 
  
          
    <p>ROSpecID:  This is the ID of the ROSpec that started, ended or got preempted.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CROSpecEvent : public CParameter
{
  public:
    CROSpecEvent (void);
    ~CROSpecEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EROSpecEventType m_eEventType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEventType;
//@}

    /** @brief Get accessor functions for the LLRP EventType field */
    inline EROSpecEventType
    getEventType (void)
    {
        return m_eEventType;
    }

    /** @brief Set accessor functions for the LLRP EventType field */
    inline void
    setEventType (
      EROSpecEventType value)
    {
        m_eEventType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_PreemptingROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPreemptingROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP PreemptingROSpecID field */
    inline llrp_u32_t
    getPreemptingROSpecID (void)
    {
        return m_PreemptingROSpecID;
    }

    /** @brief Set accessor functions for the LLRP PreemptingROSpecID field */
    inline void
    setPreemptingROSpecID (
      llrp_u32_t value)
    {
        m_PreemptingROSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CReportBufferLevelWarningEvent for LLRP parameter ReportBufferLevelWarningEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=89&view=fit>LLRP Specification Section 13.2.6.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=149&view=fit>LLRP Specification Section 16.2.7.6.4</a>
  </li>
  
</ul>  

      
          
    <p>A Reader can warn the Client that the Reader's report buffer is filling up.  A Client can act upon this warning by requesting report data from the Reader, thereby freeing the Reader's report memory resources.</p> 
 
          
    <p>A Reader 
   <b>MAY</b>
  send a report buffer level warning event whenever the Reader senses that its report memory resources are running short.  The buffer level at which a warning is reported is Reader implementation dependent.  A Client 
   <b>MAY</b>
  act upon a report buffer level warning event by requesting report data from the Reader and thereby free report memory resources in the Reader.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CReportBufferLevelWarningEvent : public CParameter
{
  public:
    CReportBufferLevelWarningEvent (void);
    ~CReportBufferLevelWarningEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u8_t m_ReportBufferPercentageFull;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReportBufferPercentageFull;
//@}

    /** @brief Get accessor functions for the LLRP ReportBufferPercentageFull field */
    inline llrp_u8_t
    getReportBufferPercentageFull (void)
    {
        return m_ReportBufferPercentageFull;
    }

    /** @brief Set accessor functions for the LLRP ReportBufferPercentageFull field */
    inline void
    setReportBufferPercentageFull (
      llrp_u8_t value)
    {
        m_ReportBufferPercentageFull = value;
    }


  
};


/**
 ** @brief  Class Definition CReportBufferOverflowErrorEvent for LLRP parameter ReportBufferOverflowErrorEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=89&view=fit>LLRP Specification Section 13.2.6.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=149&view=fit>LLRP Specification Section 16.2.7.6.5</a>
  </li>
  
</ul>  

      
           
    <p>A Reader reports a buffer overflow event whenever report data is lost due to lack of memory resources.</p> 
 
           
    <p>A Reader 
   <b>SHALL</b>
  report a buffer overflow event whenever report data is lost due to lack of memory resources.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CReportBufferOverflowErrorEvent : public CParameter
{
  public:
    CReportBufferOverflowErrorEvent (void);
    ~CReportBufferOverflowErrorEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CReaderExceptionEvent for LLRP parameter ReaderExceptionEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=90&view=fit>LLRP Specification Section 13.2.6.7</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=149&view=fit>LLRP Specification Section 16.2.7.6.6</a>
  </li>
  
</ul>  

      
          
    <p>The reader exception status event notifies the client that an unexpected event has occurred on the reader.  Optional parameters provide more detail to the client as to the nature and scope of the event.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CReaderExceptionEvent : public CParameter
{
  public:
    CReaderExceptionEvent (void);
    ~CReaderExceptionEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_utf8v_t m_Message;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMessage;
//@}

    /** @brief Get accessor functions for the LLRP Message field */
    inline llrp_utf8v_t
    getMessage (void)
    {
        return m_Message;
    }

    /** @brief Set accessor functions for the LLRP Message field */
    inline void
    setMessage (
      llrp_utf8v_t value)
    {
        m_Message = value;
    }


  
  
  
  protected:
    CROSpecID * m_pROSpecID;

  public:
    /** @brief Get accessor functions for the LLRP ROSpecID sub-parameter */  
    inline CROSpecID *
    getROSpecID (void)
    {
        return m_pROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID sub-parameter */  
    EResultCode
    setROSpecID (
      CROSpecID * pValue);


  
  
  protected:
    CSpecIndex * m_pSpecIndex;

  public:
    /** @brief Get accessor functions for the LLRP SpecIndex sub-parameter */  
    inline CSpecIndex *
    getSpecIndex (void)
    {
        return m_pSpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex sub-parameter */  
    EResultCode
    setSpecIndex (
      CSpecIndex * pValue);


  
  
  protected:
    CInventoryParameterSpecID * m_pInventoryParameterSpecID;

  public:
    /** @brief Get accessor functions for the LLRP InventoryParameterSpecID sub-parameter */  
    inline CInventoryParameterSpecID *
    getInventoryParameterSpecID (void)
    {
        return m_pInventoryParameterSpecID;
    }

    /** @brief Set accessor functions for the LLRP InventoryParameterSpecID sub-parameter */  
    EResultCode
    setInventoryParameterSpecID (
      CInventoryParameterSpecID * pValue);


  
  
  protected:
    CAntennaID * m_pAntennaID;

  public:
    /** @brief Get accessor functions for the LLRP AntennaID sub-parameter */  
    inline CAntennaID *
    getAntennaID (void)
    {
        return m_pAntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID sub-parameter */  
    EResultCode
    setAntennaID (
      CAntennaID * pValue);


  
  
  protected:
    CAccessSpecID * m_pAccessSpecID;

  public:
    /** @brief Get accessor functions for the LLRP AccessSpecID sub-parameter */  
    inline CAccessSpecID *
    getAccessSpecID (void)
    {
        return m_pAccessSpecID;
    }

    /** @brief Set accessor functions for the LLRP AccessSpecID sub-parameter */  
    EResultCode
    setAccessSpecID (
      CAccessSpecID * pValue);


  
  
  protected:
    COpSpecID * m_pOpSpecID;

  public:
    /** @brief Get accessor functions for the LLRP OpSpecID sub-parameter */  
    inline COpSpecID *
    getOpSpecID (void)
    {
        return m_pOpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID sub-parameter */  
    EResultCode
    setOpSpecID (
      COpSpecID * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition COpSpecID for LLRP parameter OpSpecID
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=90&view=fit>LLRP Specification Section 13.2.6.7.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=150&view=fit>LLRP Specification Section 16.2.7.6.6.1</a>
  </li>
  
</ul>  

      
          
    <p>Reports the OpSpecID in the reader exception event</p> 
 
       
  <HR>

    
    
  
 **/

  
  
  
class COpSpecID : public CParameter
{
  public:
    COpSpecID (void);
    ~COpSpecID (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CRFSurveyEvent for LLRP parameter RFSurveyEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=90&view=fit>LLRP Specification Section 13.2.6.8</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=150&view=fit>LLRP Specification Section 16.2.7.6.7</a>
  </li>
  
</ul>  

      
          
    <p>ROSpecID: The identifier of the ROSpec that contains the RFSurveySpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CRFSurveyEvent : public CParameter
{
  public:
    CRFSurveyEvent (void);
    ~CRFSurveyEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    ERFSurveyEventType m_eEventType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEventType;
//@}

    /** @brief Get accessor functions for the LLRP EventType field */
    inline ERFSurveyEventType
    getEventType (void)
    {
        return m_eEventType;
    }

    /** @brief Set accessor functions for the LLRP EventType field */
    inline void
    setEventType (
      ERFSurveyEventType value)
    {
        m_eEventType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_SpecIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSpecIndex;
//@}

    /** @brief Get accessor functions for the LLRP SpecIndex field */
    inline llrp_u16_t
    getSpecIndex (void)
    {
        return m_SpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex field */
    inline void
    setSpecIndex (
      llrp_u16_t value)
    {
        m_SpecIndex = value;
    }


  
};


/**
 ** @brief  Class Definition CAISpecEvent for LLRP parameter AISpecEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=91&view=fit>LLRP Specification Section 13.2.6.9</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=150&view=fit>LLRP Specification Section 16.2.7.6.8</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the AISpec event details. The EventType is the end of the AISpec. When reporting the end event, the AirProtocolSingulationDetails 
   <b>MAY</b>
  be reported if it is supported by the Reader and EventType of 7 has been enabled (Section 13.2.5.1).</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CAISpecEvent : public CParameter
{
  public:
    CAISpecEvent (void);
    ~CAISpecEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EAISpecEventType m_eEventType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEventType;
//@}

    /** @brief Get accessor functions for the LLRP EventType field */
    inline EAISpecEventType
    getEventType (void)
    {
        return m_eEventType;
    }

    /** @brief Set accessor functions for the LLRP EventType field */
    inline void
    setEventType (
      EAISpecEventType value)
    {
        m_eEventType = value;
    }


  
  
  
  protected:
    llrp_u32_t m_ROSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdROSpecID;
//@}

    /** @brief Get accessor functions for the LLRP ROSpecID field */
    inline llrp_u32_t
    getROSpecID (void)
    {
        return m_ROSpecID;
    }

    /** @brief Set accessor functions for the LLRP ROSpecID field */
    inline void
    setROSpecID (
      llrp_u32_t value)
    {
        m_ROSpecID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_SpecIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSpecIndex;
//@}

    /** @brief Get accessor functions for the LLRP SpecIndex field */
    inline llrp_u16_t
    getSpecIndex (void)
    {
        return m_SpecIndex;
    }

    /** @brief Set accessor functions for the LLRP SpecIndex field */
    inline void
    setSpecIndex (
      llrp_u16_t value)
    {
        m_SpecIndex = value;
    }


  
  
  
  protected:
    CParameter * m_pAirProtocolSingulationDetails;

  public:
    /** @brief Get accessor functions for the LLRP AirProtocolSingulationDetails sub-parameter */  
    inline CParameter *
    getAirProtocolSingulationDetails (void)
    {
        return m_pAirProtocolSingulationDetails;
    }

    /** @brief Set accessor functions for the LLRP AirProtocolSingulationDetails sub-parameter */  
    EResultCode
    setAirProtocolSingulationDetails (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CAntennaEvent for LLRP parameter AntennaEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=91&view=fit>LLRP Specification Section 13.2.6.10</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=150&view=fit>LLRP Specification Section 16.2.7.6.9</a>
  </li>
  
</ul>  

      
          
    <p>This event is generated when the Reader detects that an antenna is connected or disconnected.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CAntennaEvent : public CParameter
{
  public:
    CAntennaEvent (void);
    ~CAntennaEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EAntennaEventType m_eEventType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEventType;
//@}

    /** @brief Get accessor functions for the LLRP EventType field */
    inline EAntennaEventType
    getEventType (void)
    {
        return m_eEventType;
    }

    /** @brief Set accessor functions for the LLRP EventType field */
    inline void
    setEventType (
      EAntennaEventType value)
    {
        m_eEventType = value;
    }


  
  
  
  protected:
    llrp_u16_t m_AntennaID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAntennaID;
//@}

    /** @brief Get accessor functions for the LLRP AntennaID field */
    inline llrp_u16_t
    getAntennaID (void)
    {
        return m_AntennaID;
    }

    /** @brief Set accessor functions for the LLRP AntennaID field */
    inline void
    setAntennaID (
      llrp_u16_t value)
    {
        m_AntennaID = value;
    }


  
};


/**
 ** @brief  Class Definition CConnectionAttemptEvent for LLRP parameter ConnectionAttemptEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=92&view=fit>LLRP Specification Section 13.2.6.11</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=151&view=fit>LLRP Specification Section 16.2.7.6.10</a>
  </li>
  
</ul>  

      
          
    <p>This status report parameter establishes Reader connection status when the Client or Reader initiates a connection.  See section 18.1, TCP Transport, for more details regarding the use of this report.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CConnectionAttemptEvent : public CParameter
{
  public:
    CConnectionAttemptEvent (void);
    ~CConnectionAttemptEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EConnectionAttemptStatusType m_eStatus;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdStatus;
//@}

    /** @brief Get accessor functions for the LLRP Status field */
    inline EConnectionAttemptStatusType
    getStatus (void)
    {
        return m_eStatus;
    }

    /** @brief Set accessor functions for the LLRP Status field */
    inline void
    setStatus (
      EConnectionAttemptStatusType value)
    {
        m_eStatus = value;
    }


  
};


/**
 ** @brief  Class Definition CConnectionCloseEvent for LLRP parameter ConnectionCloseEvent
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=92&view=fit>LLRP Specification Section 13.2.6.12</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=151&view=fit>LLRP Specification Section 16.2.7.6.11</a>
  </li>
  
</ul>  

      
          
    <p>This status report parameter informs the Client that, unsolicited by the Client, the Reader will close the connection between the Reader and Client.  Before the Reader closes a connection with the Client that is not solicited by the Client, the Reader 
   <b>SHALL</b>
  first attempt to send a READER_EVENT_NOTIFICATION containing this parameter to the Client.</p> 
 
          
    <p>Once the Reader sends this event to the Client, the Reader 
   <b>SHALL</b>
  close the connection to the Client.  This is also to say that, once the Reader sends this event, the Reader 
   <b>SHALL</b>
  send no additional messages to the Client and the Reader 
   <b>SHALL</b>
  ignore any messages received from the Client until another new connection is established.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
  
 **/

  
  
  
class CConnectionCloseEvent : public CParameter
{
  public:
    CConnectionCloseEvent (void);
    ~CConnectionCloseEvent (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
};


/**
 ** @brief  Class Definition CLLRPStatus for LLRP parameter LLRPStatus
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=95&view=fit>LLRP Specification Section 14.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=151&view=fit>LLRP Specification Section 16.2.8.1</a>
  </li>
  
</ul>  

    
    
    
    
    
  
 **/

  
  
  
class CLLRPStatus : public CParameter
{
  public:
    CLLRPStatus (void);
    ~CLLRPStatus (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EStatusCode m_eStatusCode;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdStatusCode;
//@}

    /** @brief Get accessor functions for the LLRP StatusCode field */
    inline EStatusCode
    getStatusCode (void)
    {
        return m_eStatusCode;
    }

    /** @brief Set accessor functions for the LLRP StatusCode field */
    inline void
    setStatusCode (
      EStatusCode value)
    {
        m_eStatusCode = value;
    }


  
  
  
  protected:
    llrp_utf8v_t m_ErrorDescription;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdErrorDescription;
//@}

    /** @brief Get accessor functions for the LLRP ErrorDescription field */
    inline llrp_utf8v_t
    getErrorDescription (void)
    {
        return m_ErrorDescription;
    }

    /** @brief Set accessor functions for the LLRP ErrorDescription field */
    inline void
    setErrorDescription (
      llrp_utf8v_t value)
    {
        m_ErrorDescription = value;
    }


  
  
  
  protected:
    CFieldError * m_pFieldError;

  public:
    /** @brief Get accessor functions for the LLRP FieldError sub-parameter */  
    inline CFieldError *
    getFieldError (void)
    {
        return m_pFieldError;
    }

    /** @brief Set accessor functions for the LLRP FieldError sub-parameter */  
    EResultCode
    setFieldError (
      CFieldError * pValue);


  
  
  protected:
    CParameterError * m_pParameterError;

  public:
    /** @brief Get accessor functions for the LLRP ParameterError sub-parameter */  
    inline CParameterError *
    getParameterError (void)
    {
        return m_pParameterError;
    }

    /** @brief Set accessor functions for the LLRP ParameterError sub-parameter */  
    EResultCode
    setParameterError (
      CParameterError * pValue);


};


/**
 ** @brief  Class Definition CFieldError for LLRP parameter FieldError
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=96&view=fit>LLRP Specification Section 14.2.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=151&view=fit>LLRP Specification Section 16.2.8.1.1</a>
  </li>
  
</ul>  

      
          
    <p>FieldNum: Field number for which the error applies. The fields are numbered after the order in which they appear in the parameter or message body.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CFieldError : public CParameter
{
  public:
    CFieldError (void);
    ~CFieldError (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_FieldNum;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdFieldNum;
//@}

    /** @brief Get accessor functions for the LLRP FieldNum field */
    inline llrp_u16_t
    getFieldNum (void)
    {
        return m_FieldNum;
    }

    /** @brief Set accessor functions for the LLRP FieldNum field */
    inline void
    setFieldNum (
      llrp_u16_t value)
    {
        m_FieldNum = value;
    }


  
  
  
  protected:
    EStatusCode m_eErrorCode;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdErrorCode;
//@}

    /** @brief Get accessor functions for the LLRP ErrorCode field */
    inline EStatusCode
    getErrorCode (void)
    {
        return m_eErrorCode;
    }

    /** @brief Set accessor functions for the LLRP ErrorCode field */
    inline void
    setErrorCode (
      EStatusCode value)
    {
        m_eErrorCode = value;
    }


  
};


/**
 ** @brief  Class Definition CParameterError for LLRP parameter ParameterError
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=96&view=fit>LLRP Specification Section 14.2.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=152&view=fit>LLRP Specification Section 16.2.8.1.2</a>
  </li>
  
</ul>  

      
          
    <p>The parameter type that caused this error.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CParameterError : public CParameter
{
  public:
    CParameterError (void);
    ~CParameterError (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_ParameterType;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdParameterType;
//@}

    /** @brief Get accessor functions for the LLRP ParameterType field */
    inline llrp_u16_t
    getParameterType (void)
    {
        return m_ParameterType;
    }

    /** @brief Set accessor functions for the LLRP ParameterType field */
    inline void
    setParameterType (
      llrp_u16_t value)
    {
        m_ParameterType = value;
    }


  
  
  
  protected:
    EStatusCode m_eErrorCode;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdErrorCode;
//@}

    /** @brief Get accessor functions for the LLRP ErrorCode field */
    inline EStatusCode
    getErrorCode (void)
    {
        return m_eErrorCode;
    }

    /** @brief Set accessor functions for the LLRP ErrorCode field */
    inline void
    setErrorCode (
      EStatusCode value)
    {
        m_eErrorCode = value;
    }


  
  
  
  protected:
    CFieldError * m_pFieldError;

  public:
    /** @brief Get accessor functions for the LLRP FieldError sub-parameter */  
    inline CFieldError *
    getFieldError (void)
    {
        return m_pFieldError;
    }

    /** @brief Set accessor functions for the LLRP FieldError sub-parameter */  
    EResultCode
    setFieldError (
      CFieldError * pValue);


  
  
  protected:
    CParameterError * m_pParameterError;

  public:
    /** @brief Get accessor functions for the LLRP ParameterError sub-parameter */  
    inline CParameterError *
    getParameterError (void)
    {
        return m_pParameterError;
    }

    /** @brief Set accessor functions for the LLRP ParameterError sub-parameter */  
    EResultCode
    setParameterError (
      CParameterError * pValue);


};


/**
 ** @brief  Class Definition CC1G2LLRPCapabilities for LLRP parameter C1G2LLRPCapabilities
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=98&view=fit>LLRP Specification Section 15.2.1.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=153&view=fit>LLRP Specification Section 16.3.1.1.1</a>
  </li>
  
</ul>  

      
          
    <p>Readers 
   <b>MAY</b>
  support BlockErase, and 
   <b>MAY</b>
  support BlockWrite. Readers 
   <b>SHALL</b>
  support at least one select filter per query. </p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
  
 **/

  
  
  
class CC1G2LLRPCapabilities : public CParameter
{
  public:
    CC1G2LLRPCapabilities (void);
    ~CC1G2LLRPCapabilities (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_CanSupportBlockErase;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanSupportBlockErase;
//@}

    /** @brief Get accessor functions for the LLRP CanSupportBlockErase field */
    inline llrp_u1_t
    getCanSupportBlockErase (void)
    {
        return m_CanSupportBlockErase;
    }

    /** @brief Set accessor functions for the LLRP CanSupportBlockErase field */
    inline void
    setCanSupportBlockErase (
      llrp_u1_t value)
    {
        m_CanSupportBlockErase = value;
    }


  
  
  
  protected:
    llrp_u1_t m_CanSupportBlockWrite;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCanSupportBlockWrite;
//@}

    /** @brief Get accessor functions for the LLRP CanSupportBlockWrite field */
    inline llrp_u1_t
    getCanSupportBlockWrite (void)
    {
        return m_CanSupportBlockWrite;
    }

    /** @brief Set accessor functions for the LLRP CanSupportBlockWrite field */
    inline void
    setCanSupportBlockWrite (
      llrp_u1_t value)
    {
        m_CanSupportBlockWrite = value;
    }


  
  
  
  protected:
    llrp_u16_t m_MaxNumSelectFiltersPerQuery;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxNumSelectFiltersPerQuery;
//@}

    /** @brief Get accessor functions for the LLRP MaxNumSelectFiltersPerQuery field */
    inline llrp_u16_t
    getMaxNumSelectFiltersPerQuery (void)
    {
        return m_MaxNumSelectFiltersPerQuery;
    }

    /** @brief Set accessor functions for the LLRP MaxNumSelectFiltersPerQuery field */
    inline void
    setMaxNumSelectFiltersPerQuery (
      llrp_u16_t value)
    {
        m_MaxNumSelectFiltersPerQuery = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2UHFRFModeTable for LLRP parameter C1G2UHFRFModeTable
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=98&view=fit>LLRP Specification Section 15.2.1.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=153&view=fit>LLRP Specification Section 16.3.1.1.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the set of C1G2 RF modes that the Reader is capable of operating.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CC1G2UHFRFModeTable : public CParameter
{
  public:
    CC1G2UHFRFModeTable (void);
    ~CC1G2UHFRFModeTable (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    std::list<CC1G2UHFRFModeTableEntry *> m_listC1G2UHFRFModeTableEntry;

  public:
     /** @brief  Returns the first element of the C1G2UHFRFModeTableEntry sub-parameter list*/  
    inline std::list<CC1G2UHFRFModeTableEntry *>::iterator
    beginC1G2UHFRFModeTableEntry (void)
    {
        return m_listC1G2UHFRFModeTableEntry.begin();
    }

     /** @brief  Returns the last element of the C1G2UHFRFModeTableEntry sub-parameter list*/  
    inline std::list<CC1G2UHFRFModeTableEntry *>::iterator
    endC1G2UHFRFModeTableEntry (void)
    {
        return m_listC1G2UHFRFModeTableEntry.end();
    }

     /** @brief  Clears the LLRP C1G2UHFRFModeTableEntry sub-parameter list*/  
    inline void
    clearC1G2UHFRFModeTableEntry (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listC1G2UHFRFModeTableEntry);
    }

     /** @brief  Count of the LLRP C1G2UHFRFModeTableEntry sub-parameter list*/  
    inline int
    countC1G2UHFRFModeTableEntry (void)
    {
        return (int) (m_listC1G2UHFRFModeTableEntry.size());
    }

    EResultCode
     /** @brief  Add a C1G2UHFRFModeTableEntry to the LLRP sub-parameter list*/  
    addC1G2UHFRFModeTableEntry (
      CC1G2UHFRFModeTableEntry * pValue);


};


/**
 ** @brief  Class Definition CC1G2UHFRFModeTableEntry for LLRP parameter C1G2UHFRFModeTableEntry
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=99&view=fit>LLRP Specification Section 15.2.1.1.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=153&view=fit>LLRP Specification Section 16.3.1.1.2.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries the information for each UHFC1G2 RF mode. A mode that has been tested for conformance by the EPCGlobal Hardware Action Group's Testing and Conformance (HAG T and C) group, is indicated using a conformance flag.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2UHFRFModeTableEntry : public CParameter
{
  public:
    CC1G2UHFRFModeTableEntry (void);
    ~CC1G2UHFRFModeTableEntry (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u32_t m_ModeIdentifier;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdModeIdentifier;
//@}

    /** @brief Get accessor functions for the LLRP ModeIdentifier field */
    inline llrp_u32_t
    getModeIdentifier (void)
    {
        return m_ModeIdentifier;
    }

    /** @brief Set accessor functions for the LLRP ModeIdentifier field */
    inline void
    setModeIdentifier (
      llrp_u32_t value)
    {
        m_ModeIdentifier = value;
    }


  
  
  
  protected:
    EC1G2DRValue m_eDRValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDRValue;
//@}

    /** @brief Get accessor functions for the LLRP DRValue field */
    inline EC1G2DRValue
    getDRValue (void)
    {
        return m_eDRValue;
    }

    /** @brief Set accessor functions for the LLRP DRValue field */
    inline void
    setDRValue (
      EC1G2DRValue value)
    {
        m_eDRValue = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EPCHAGTCConformance;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEPCHAGTCConformance;
//@}

    /** @brief Get accessor functions for the LLRP EPCHAGTCConformance field */
    inline llrp_u1_t
    getEPCHAGTCConformance (void)
    {
        return m_EPCHAGTCConformance;
    }

    /** @brief Set accessor functions for the LLRP EPCHAGTCConformance field */
    inline void
    setEPCHAGTCConformance (
      llrp_u1_t value)
    {
        m_EPCHAGTCConformance = value;
    }


  
  
  
  protected:
    EC1G2MValue m_eMValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMValue;
//@}

    /** @brief Get accessor functions for the LLRP MValue field */
    inline EC1G2MValue
    getMValue (void)
    {
        return m_eMValue;
    }

    /** @brief Set accessor functions for the LLRP MValue field */
    inline void
    setMValue (
      EC1G2MValue value)
    {
        m_eMValue = value;
    }


  
  
  
  protected:
    EC1G2ForwardLinkModulation m_eForwardLinkModulation;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdForwardLinkModulation;
//@}

    /** @brief Get accessor functions for the LLRP ForwardLinkModulation field */
    inline EC1G2ForwardLinkModulation
    getForwardLinkModulation (void)
    {
        return m_eForwardLinkModulation;
    }

    /** @brief Set accessor functions for the LLRP ForwardLinkModulation field */
    inline void
    setForwardLinkModulation (
      EC1G2ForwardLinkModulation value)
    {
        m_eForwardLinkModulation = value;
    }


  
  
  
  protected:
    EC1G2SpectralMaskIndicator m_eSpectralMaskIndicator;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSpectralMaskIndicator;
//@}

    /** @brief Get accessor functions for the LLRP SpectralMaskIndicator field */
    inline EC1G2SpectralMaskIndicator
    getSpectralMaskIndicator (void)
    {
        return m_eSpectralMaskIndicator;
    }

    /** @brief Set accessor functions for the LLRP SpectralMaskIndicator field */
    inline void
    setSpectralMaskIndicator (
      EC1G2SpectralMaskIndicator value)
    {
        m_eSpectralMaskIndicator = value;
    }


  
  
  
  protected:
    llrp_u32_t m_BDRValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdBDRValue;
//@}

    /** @brief Get accessor functions for the LLRP BDRValue field */
    inline llrp_u32_t
    getBDRValue (void)
    {
        return m_BDRValue;
    }

    /** @brief Set accessor functions for the LLRP BDRValue field */
    inline void
    setBDRValue (
      llrp_u32_t value)
    {
        m_BDRValue = value;
    }


  
  
  
  protected:
    llrp_u32_t m_PIEValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPIEValue;
//@}

    /** @brief Get accessor functions for the LLRP PIEValue field */
    inline llrp_u32_t
    getPIEValue (void)
    {
        return m_PIEValue;
    }

    /** @brief Set accessor functions for the LLRP PIEValue field */
    inline void
    setPIEValue (
      llrp_u32_t value)
    {
        m_PIEValue = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MinTariValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMinTariValue;
//@}

    /** @brief Get accessor functions for the LLRP MinTariValue field */
    inline llrp_u32_t
    getMinTariValue (void)
    {
        return m_MinTariValue;
    }

    /** @brief Set accessor functions for the LLRP MinTariValue field */
    inline void
    setMinTariValue (
      llrp_u32_t value)
    {
        m_MinTariValue = value;
    }


  
  
  
  protected:
    llrp_u32_t m_MaxTariValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMaxTariValue;
//@}

    /** @brief Get accessor functions for the LLRP MaxTariValue field */
    inline llrp_u32_t
    getMaxTariValue (void)
    {
        return m_MaxTariValue;
    }

    /** @brief Set accessor functions for the LLRP MaxTariValue field */
    inline void
    setMaxTariValue (
      llrp_u32_t value)
    {
        m_MaxTariValue = value;
    }


  
  
  
  protected:
    llrp_u32_t m_StepTariValue;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdStepTariValue;
//@}

    /** @brief Get accessor functions for the LLRP StepTariValue field */
    inline llrp_u32_t
    getStepTariValue (void)
    {
        return m_StepTariValue;
    }

    /** @brief Set accessor functions for the LLRP StepTariValue field */
    inline void
    setStepTariValue (
      llrp_u32_t value)
    {
        m_StepTariValue = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2InventoryCommand for LLRP parameter C1G2InventoryCommand
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=100&view=fit>LLRP Specification Section 15.2.1.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=154&view=fit>LLRP Specification Section 16.3.1.2.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter defines the C1G2 inventory-specific settings to be used during a particular C1G2 inventory operation. This comprises of C1G2Filter Parameter, C1G2RF Parameter and C1G2Singulation Parameter. It is not necessary that the Filter, RF Control and Singulation Control Parameters be specified in each and every inventory command. They are optional parameters. If not specified, the default values in the Reader are used during the inventory operation. If multiple C1G2Filter parameters are encapsulated by the Client in the C1G2InventoryCommand parameter, the ordering of the filter parameters determine the order of C1G2 air-protocol commands (e.g., Select command) generated by the Reader.</p> 
 
          
    <p>The TagInventoryStateAware flag is used to determine how to process all the C1G2Filter and C1G2Singulation parameters in this command. At a functional level, if the Client is managing the tag states during an inventory operation, it would set that flag to true and pass the appropriate fields in the C1G2 Filter and C1G2 Singulation parameters. If a reader set CanDoTagInventoryStateAwareSingulation to False in LLRPCapabilities (section 9.2.2), it 
   <b>SHALL</b>
  ignore the TagInventoryStateAware flag.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2InventoryCommand : public CParameter
{
  public:
    CC1G2InventoryCommand (void);
    ~CC1G2InventoryCommand (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_TagInventoryStateAware;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagInventoryStateAware;
//@}

    /** @brief Get accessor functions for the LLRP TagInventoryStateAware field */
    inline llrp_u1_t
    getTagInventoryStateAware (void)
    {
        return m_TagInventoryStateAware;
    }

    /** @brief Set accessor functions for the LLRP TagInventoryStateAware field */
    inline void
    setTagInventoryStateAware (
      llrp_u1_t value)
    {
        m_TagInventoryStateAware = value;
    }


  
  
  
  protected:
    std::list<CC1G2Filter *> m_listC1G2Filter;

  public:
     /** @brief  Returns the first element of the C1G2Filter sub-parameter list*/  
    inline std::list<CC1G2Filter *>::iterator
    beginC1G2Filter (void)
    {
        return m_listC1G2Filter.begin();
    }

     /** @brief  Returns the last element of the C1G2Filter sub-parameter list*/  
    inline std::list<CC1G2Filter *>::iterator
    endC1G2Filter (void)
    {
        return m_listC1G2Filter.end();
    }

     /** @brief  Clears the LLRP C1G2Filter sub-parameter list*/  
    inline void
    clearC1G2Filter (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listC1G2Filter);
    }

     /** @brief  Count of the LLRP C1G2Filter sub-parameter list*/  
    inline int
    countC1G2Filter (void)
    {
        return (int) (m_listC1G2Filter.size());
    }

    EResultCode
     /** @brief  Add a C1G2Filter to the LLRP sub-parameter list*/  
    addC1G2Filter (
      CC1G2Filter * pValue);


  
  
  protected:
    CC1G2RFControl * m_pC1G2RFControl;

  public:
    /** @brief Get accessor functions for the LLRP C1G2RFControl sub-parameter */  
    inline CC1G2RFControl *
    getC1G2RFControl (void)
    {
        return m_pC1G2RFControl;
    }

    /** @brief Set accessor functions for the LLRP C1G2RFControl sub-parameter */  
    EResultCode
    setC1G2RFControl (
      CC1G2RFControl * pValue);


  
  
  protected:
    CC1G2SingulationControl * m_pC1G2SingulationControl;

  public:
    /** @brief Get accessor functions for the LLRP C1G2SingulationControl sub-parameter */  
    inline CC1G2SingulationControl *
    getC1G2SingulationControl (void)
    {
        return m_pC1G2SingulationControl;
    }

    /** @brief Set accessor functions for the LLRP C1G2SingulationControl sub-parameter */  
    EResultCode
    setC1G2SingulationControl (
      CC1G2SingulationControl * pValue);


  
  
  protected:
    std::list<CParameter *> m_listCustom;

  public:
     /** @brief  Returns the first element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    beginCustom (void)
    {
        return m_listCustom.begin();
    }

     /** @brief  Returns the last element of the Custom sub-parameter list*/  
    inline std::list<CParameter *>::iterator
    endCustom (void)
    {
        return m_listCustom.end();
    }

     /** @brief  Clears the LLRP Custom sub-parameter list*/  
    inline void
    clearCustom (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listCustom);
    }

     /** @brief  Count of the LLRP Custom sub-parameter list*/  
    inline int
    countCustom (void)
    {
        return (int) (m_listCustom.size());
    }

    EResultCode
     /** @brief  Add a Custom to the LLRP sub-parameter list*/  
    addCustom (
      CParameter * pValue);


};


/**
 ** @brief  Class Definition CC1G2Filter for LLRP parameter C1G2Filter
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=101&view=fit>LLRP Specification Section 15.2.1.2.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=154&view=fit>LLRP Specification Section 16.3.1.2.1.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter carries information specific to C1G2 filter (in particular, the parameters for the select command) operation, and are optionally sent with each inventory command from the Client to the Reader. This sets up the target tag population that gets inventoried. For an inventory operation with multiple filters, multiple instances of filter parameters are sent. A filter parameter contains the following fields:</p> 
 
          
    <ul>
             
    <li>
    <p>Target tag mask: This contains the information for the tag memory data pattern used for the select operation.</p> 
 </li>
  
             
    <li>
    <p>T:  This value is set if the Client is interested in only a truncated portion of the tag to be backscattered by the tag. The portion that gets backscattered includes the portion of the tag ID following the mask. This bit has to be set only in the last filter-spec.</p> 
 </li>
 
             
    <li>
    <p>TagInventoryStateAwareFilterAction: This is used if the TagInventoryStateAware flag is set to true in the InventoryParameterSpec. </p> 
 </li>
 
             
    <li>
    <p>TagInventoryStateUnawareFilterAction: This is used if the TagInventoryStateAware flag is set to false in the InventoryParameterSpec.</p> 
 </li>
 
         </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2Filter : public CParameter
{
  public:
    CC1G2Filter (void);
    ~CC1G2Filter (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2TruncateAction m_eT;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdT;
//@}

    /** @brief Get accessor functions for the LLRP T field */
    inline EC1G2TruncateAction
    getT (void)
    {
        return m_eT;
    }

    /** @brief Set accessor functions for the LLRP T field */
    inline void
    setT (
      EC1G2TruncateAction value)
    {
        m_eT = value;
    }


  
  
  
  protected:
    CC1G2TagInventoryMask * m_pC1G2TagInventoryMask;

  public:
    /** @brief Get accessor functions for the LLRP C1G2TagInventoryMask sub-parameter */  
    inline CC1G2TagInventoryMask *
    getC1G2TagInventoryMask (void)
    {
        return m_pC1G2TagInventoryMask;
    }

    /** @brief Set accessor functions for the LLRP C1G2TagInventoryMask sub-parameter */  
    EResultCode
    setC1G2TagInventoryMask (
      CC1G2TagInventoryMask * pValue);


  
  
  protected:
    CC1G2TagInventoryStateAwareFilterAction * m_pC1G2TagInventoryStateAwareFilterAction;

  public:
    /** @brief Get accessor functions for the LLRP C1G2TagInventoryStateAwareFilterAction sub-parameter */  
    inline CC1G2TagInventoryStateAwareFilterAction *
    getC1G2TagInventoryStateAwareFilterAction (void)
    {
        return m_pC1G2TagInventoryStateAwareFilterAction;
    }

    /** @brief Set accessor functions for the LLRP C1G2TagInventoryStateAwareFilterAction sub-parameter */  
    EResultCode
    setC1G2TagInventoryStateAwareFilterAction (
      CC1G2TagInventoryStateAwareFilterAction * pValue);


  
  
  protected:
    CC1G2TagInventoryStateUnawareFilterAction * m_pC1G2TagInventoryStateUnawareFilterAction;

  public:
    /** @brief Get accessor functions for the LLRP C1G2TagInventoryStateUnawareFilterAction sub-parameter */  
    inline CC1G2TagInventoryStateUnawareFilterAction *
    getC1G2TagInventoryStateUnawareFilterAction (void)
    {
        return m_pC1G2TagInventoryStateUnawareFilterAction;
    }

    /** @brief Set accessor functions for the LLRP C1G2TagInventoryStateUnawareFilterAction sub-parameter */  
    EResultCode
    setC1G2TagInventoryStateUnawareFilterAction (
      CC1G2TagInventoryStateUnawareFilterAction * pValue);


};


/**
 ** @brief  Class Definition CC1G2TagInventoryMask for LLRP parameter C1G2TagInventoryMask
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=102&view=fit>LLRP Specification Section 15.2.1.2.1.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=154&view=fit>LLRP Specification Section 16.3.1.2.1.1.1</a>
  </li>
  
</ul>  

    
    
    
    
    
  
 **/

  
  
  
class CC1G2TagInventoryMask : public CParameter
{
  public:
    CC1G2TagInventoryMask (void);
    ~CC1G2TagInventoryMask (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u16_t m_Pointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPointer;
//@}

    /** @brief Get accessor functions for the LLRP Pointer field */
    inline llrp_u16_t
    getPointer (void)
    {
        return m_Pointer;
    }

    /** @brief Set accessor functions for the LLRP Pointer field */
    inline void
    setPointer (
      llrp_u16_t value)
    {
        m_Pointer = value;
    }


  
  
  
  protected:
    llrp_u1v_t m_TagMask;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagMask;
//@}

    /** @brief Get accessor functions for the LLRP TagMask field */
    inline llrp_u1v_t
    getTagMask (void)
    {
        return m_TagMask;
    }

    /** @brief Set accessor functions for the LLRP TagMask field */
    inline void
    setTagMask (
      llrp_u1v_t value)
    {
        m_TagMask = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2TagInventoryStateAwareFilterAction for LLRP parameter C1G2TagInventoryStateAwareFilterAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=102&view=fit>LLRP Specification Section 15.2.1.2.1.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=155&view=fit>LLRP Specification Section 16.3.1.2.1.1.2</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used by the Client to manage the tag states during an inventory operation.  In order to use this parameter during inventory, the TagInventoryStateAware flag is set to true in the InventoryParameterSpec. This parameter contains:</p> 
 
          
    <ul>
             
    <li>
    <p>Target: This value indicates which flag in the tag to modify - whether the SL flag or its inventoried flag for a particular session.</p> 
 </li>
 
             
    <li>
    <p>Action describes the action for matching and non-matching tags. The actions are specific about the tag-inventory states - e.g., do nothing, assert or deassert SL, assign inventoried S0/S1/S2/S3 to A or B.</p> 
 </li>
 
            
    <p>Readers that do not support tag inventory state aware singulation 
   <b>SHALL</b>
  set CanDoTagInventoryStateAwareSingulation to false in LLRPCapabilities</p> 
 
          </ul> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2TagInventoryStateAwareFilterAction : public CParameter
{
  public:
    CC1G2TagInventoryStateAwareFilterAction (void);
    ~CC1G2TagInventoryStateAwareFilterAction (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2StateAwareTarget m_eTarget;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTarget;
//@}

    /** @brief Get accessor functions for the LLRP Target field */
    inline EC1G2StateAwareTarget
    getTarget (void)
    {
        return m_eTarget;
    }

    /** @brief Set accessor functions for the LLRP Target field */
    inline void
    setTarget (
      EC1G2StateAwareTarget value)
    {
        m_eTarget = value;
    }


  
  
  
  protected:
    EC1G2StateAwareAction m_eAction;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAction;
//@}

    /** @brief Get accessor functions for the LLRP Action field */
    inline EC1G2StateAwareAction
    getAction (void)
    {
        return m_eAction;
    }

    /** @brief Set accessor functions for the LLRP Action field */
    inline void
    setAction (
      EC1G2StateAwareAction value)
    {
        m_eAction = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2TagInventoryStateUnawareFilterAction for LLRP parameter C1G2TagInventoryStateUnawareFilterAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=103&view=fit>LLRP Specification Section 15.2.1.2.1.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=155&view=fit>LLRP Specification Section 16.3.1.2.1.1.3</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used by the Client if it does not want to manage the tag states during an inventory operation. Using this parameter, the Client instructs the Reader about the tags that should and should not participate in the inventory action.  In order to use this parameter during inventory, the TagInventoryStateAware flag is set to false in the InventoryParameterSpec. This parameter contains:</p> 
 
            
    <ul>
              
    <li>
    <p>Action describes the action for matching and non-matching tags. However, the action is simply specifying whether matching or non-matching tags partake in this inventory. The Reader is expected to handle the tag inventory states to facilitate this.</p> 
 </li>
 
            </ul> 
 
          
    <p>In this parameter, Action=Select means search for pattern in Inventory, and Action=Unselect means do not search for pattern in Inventory.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CC1G2TagInventoryStateUnawareFilterAction : public CParameter
{
  public:
    CC1G2TagInventoryStateUnawareFilterAction (void);
    ~CC1G2TagInventoryStateUnawareFilterAction (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2StateUnawareAction m_eAction;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAction;
//@}

    /** @brief Get accessor functions for the LLRP Action field */
    inline EC1G2StateUnawareAction
    getAction (void)
    {
        return m_eAction;
    }

    /** @brief Set accessor functions for the LLRP Action field */
    inline void
    setAction (
      EC1G2StateUnawareAction value)
    {
        m_eAction = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2RFControl for LLRP parameter C1G2RFControl
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=104&view=fit>LLRP Specification Section 15.2.1.2.1.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=155&view=fit>LLRP Specification Section 16.3.1.2.1.2</a>
  </li>
  
</ul>  

      
          
    <p>This Parameter carries the settings relevant to RF forward and reverse link control in the C1G2 air protocol. This is basically the C1G2 RF Mode and the Tari value to use for the inventory operation.</p> 
 
          
    <p>Tari: Value of Tari to use for this mode specified in nsec. This is specified if the mode selected has a Tari range. If the selected mode has a range, and the Tari is set to zero, the Reader implementation picks up any Tari value within the range. If the selected mode has a range, and the specified Tari is out of that range and is not set to zero, an error message is generated.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2RFControl : public CParameter
{
  public:
    CC1G2RFControl (void);
    ~CC1G2RFControl (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_ModeIndex;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdModeIndex;
//@}

    /** @brief Get accessor functions for the LLRP ModeIndex field */
    inline llrp_u16_t
    getModeIndex (void)
    {
        return m_ModeIndex;
    }

    /** @brief Set accessor functions for the LLRP ModeIndex field */
    inline void
    setModeIndex (
      llrp_u16_t value)
    {
        m_ModeIndex = value;
    }


  
  
  
  protected:
    llrp_u16_t m_Tari;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTari;
//@}

    /** @brief Get accessor functions for the LLRP Tari field */
    inline llrp_u16_t
    getTari (void)
    {
        return m_Tari;
    }

    /** @brief Set accessor functions for the LLRP Tari field */
    inline void
    setTari (
      llrp_u16_t value)
    {
        m_Tari = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2SingulationControl for LLRP parameter C1G2SingulationControl
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=104&view=fit>LLRP Specification Section 15.2.1.2.1.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=155&view=fit>LLRP Specification Section 16.3.1.2.1.3</a>
  </li>
  
</ul>  

      
          
    <p>This C1G2SingulationControl Parameter provides controls particular to the singulation process in the C1G2 air protocol. The singulation process is started using a Query command in the C1G2 protocol. The Query command describes the session number, tag state, the start Q value to use, and the RF link parameters. The RF link parameters are specified using the C1G2RFControl Parameter (see section 15.2.1.2.1.2). This Singulation Parameter specifies the session, tag state and description of the target singulation environment. The following attributes are specified to provide guidance to the Reader for the singulation algorithm:</p> 
   
          
    <ul>
             
    <li>
    <p>Tag transit time: This is the measure of expected tag mobility in the field of view of the antenna where this inventory operation is getting executed.</p> 
 </li>
 
             
    <li>
    <p>Tag population: This is the expected tag population in the field of view of the antenna.</p> 
 </li>
 
          </ul> 
      
          
    <p>In addition, the Singulation Parameter allows setting of the following:</p> 
 
          
    <ul>
            
    <li>
    <p>Session ID: This is the C1G2 session number that the tags use to update the inventory state upon successful singulation.</p> 
 </li>
 
            
    <li>
    <p>TagInventoryStateAwareSingulationAction: This is used if the TagInventoryStateAware flag is set to true in the InventoryParameterSpec.</p> 
 
               
    <ul> 
                  
    <li>
    <p>    I: This is the inventoried state of the target tag population in the selected session. Only tags that match the session state participate in the inventory round.  If the Ignore value is specified, the Reader ignores this field, and its up to the Reader implementation to determine the value of I used in the inventory round.</p> 
 </li>
 
                  
    <li>
    <p>    S: This is the state of the SL flag in the tag. Only tags that match that tag state participate in the inventory round. If the Ignore value is specified, the Reader ignores this field, and its up to the Reader implementation to determine the value of S used in the inventory round.</p> 
 </li>
 
                </ul> 
 </li>
 
          </ul> 
 
          
    <p>If a reader sets CanDoTagInventoryStateAwareSingulation to False in LLRPCapabilities (section 9.2.2), it 
   <b>SHALL</b>
  ignore the TagInventoryStateAwareSingulationAction field.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2SingulationControl : public CParameter
{
  public:
    CC1G2SingulationControl (void);
    ~CC1G2SingulationControl (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u2_t m_Session;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdSession;
//@}

    /** @brief Get accessor functions for the LLRP Session field */
    inline llrp_u2_t
    getSession (void)
    {
        return m_Session;
    }

    /** @brief Set accessor functions for the LLRP Session field */
    inline void
    setSession (
      llrp_u2_t value)
    {
        m_Session = value;
    }


  
  
  
  protected:
    llrp_u16_t m_TagPopulation;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagPopulation;
//@}

    /** @brief Get accessor functions for the LLRP TagPopulation field */
    inline llrp_u16_t
    getTagPopulation (void)
    {
        return m_TagPopulation;
    }

    /** @brief Set accessor functions for the LLRP TagPopulation field */
    inline void
    setTagPopulation (
      llrp_u16_t value)
    {
        m_TagPopulation = value;
    }


  
  
  
  protected:
    llrp_u32_t m_TagTransitTime;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagTransitTime;
//@}

    /** @brief Get accessor functions for the LLRP TagTransitTime field */
    inline llrp_u32_t
    getTagTransitTime (void)
    {
        return m_TagTransitTime;
    }

    /** @brief Set accessor functions for the LLRP TagTransitTime field */
    inline void
    setTagTransitTime (
      llrp_u32_t value)
    {
        m_TagTransitTime = value;
    }


  
  
  
  protected:
    CC1G2TagInventoryStateAwareSingulationAction * m_pC1G2TagInventoryStateAwareSingulationAction;

  public:
    /** @brief Get accessor functions for the LLRP C1G2TagInventoryStateAwareSingulationAction sub-parameter */  
    inline CC1G2TagInventoryStateAwareSingulationAction *
    getC1G2TagInventoryStateAwareSingulationAction (void)
    {
        return m_pC1G2TagInventoryStateAwareSingulationAction;
    }

    /** @brief Set accessor functions for the LLRP C1G2TagInventoryStateAwareSingulationAction sub-parameter */  
    EResultCode
    setC1G2TagInventoryStateAwareSingulationAction (
      CC1G2TagInventoryStateAwareSingulationAction * pValue);


};


/**
 ** @brief  Class Definition CC1G2TagInventoryStateAwareSingulationAction for LLRP parameter C1G2TagInventoryStateAwareSingulationAction
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=105&view=fit>LLRP Specification Section 15.2.1.2.1.3.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=156&view=fit>LLRP Specification Section 16.3.1.2.1.3.1</a>
  </li>
  
</ul>  

      
          Readers that do not support tag inventory state aware singulation 
   <b>SHALL</b>
  set CanDoTagInventoryStateAwareSingulation to false in LLRPCapabilities.
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
        
    
  
 **/

  
  
  
class CC1G2TagInventoryStateAwareSingulationAction : public CParameter
{
  public:
    CC1G2TagInventoryStateAwareSingulationAction (void);
    ~CC1G2TagInventoryStateAwareSingulationAction (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2TagInventoryStateAwareI m_eI;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdI;
//@}

    /** @brief Get accessor functions for the LLRP I field */
    inline EC1G2TagInventoryStateAwareI
    getI (void)
    {
        return m_eI;
    }

    /** @brief Set accessor functions for the LLRP I field */
    inline void
    setI (
      EC1G2TagInventoryStateAwareI value)
    {
        m_eI = value;
    }


  
  
  
  protected:
    EC1G2TagInventoryStateAwareS m_eS;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdS;
//@}

    /** @brief Get accessor functions for the LLRP S field */
    inline EC1G2TagInventoryStateAwareS
    getS (void)
    {
        return m_eS;
    }

    /** @brief Set accessor functions for the LLRP S field */
    inline void
    setS (
      EC1G2TagInventoryStateAwareS value)
    {
        m_eS = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2TagSpec for LLRP parameter C1G2TagSpec
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=106&view=fit>LLRP Specification Section 15.2.1.3.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=156&view=fit>LLRP Specification Section 16.3.1.3.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter describes the target tag population on which certain operations have to be performed.  This Parameter is similar to the selection C1G2Filter Parameter described earlier. However, because these tags are stored in the Reader's memory and ternary comparisons are to be allowed for, each bit i in the target tag is represented using 2 bits - bit i in mask, and bit i in tag pattern.  If bit i in the mask is zero, then bit i of the target tag is a don't care (X); if bit i in the mask is one, then bit i of the target tag is bit i of the tag pattern. For example, "all tags" is specified using a mask length of zero.</p> 
 
          
    <p>This parameter can carry up to two tag patterns. If more than one pattern is present, a Boolean AND is implied. Each tag pattern has a match or a non-match flag, allowing (A and B,!A and B, !A and !B, A and !B), where A and B are the tag patterns.</p> 
 
          
    <p>The tagSpec contains 2 tag patterns.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
  
 **/

  
  
  
class CC1G2TagSpec : public CParameter
{
  public:
    CC1G2TagSpec (void);
    ~CC1G2TagSpec (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    std::list<CC1G2TargetTag *> m_listC1G2TargetTag;

  public:
     /** @brief  Returns the first element of the C1G2TargetTag sub-parameter list*/  
    inline std::list<CC1G2TargetTag *>::iterator
    beginC1G2TargetTag (void)
    {
        return m_listC1G2TargetTag.begin();
    }

     /** @brief  Returns the last element of the C1G2TargetTag sub-parameter list*/  
    inline std::list<CC1G2TargetTag *>::iterator
    endC1G2TargetTag (void)
    {
        return m_listC1G2TargetTag.end();
    }

     /** @brief  Clears the LLRP C1G2TargetTag sub-parameter list*/  
    inline void
    clearC1G2TargetTag (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listC1G2TargetTag);
    }

     /** @brief  Count of the LLRP C1G2TargetTag sub-parameter list*/  
    inline int
    countC1G2TargetTag (void)
    {
        return (int) (m_listC1G2TargetTag.size());
    }

    EResultCode
     /** @brief  Add a C1G2TargetTag to the LLRP sub-parameter list*/  
    addC1G2TargetTag (
      CC1G2TargetTag * pValue);


};


/**
 ** @brief  Class Definition CC1G2TargetTag for LLRP parameter C1G2TargetTag
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=106&view=fit>LLRP Specification Section 15.2.1.3.1.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=156&view=fit>LLRP Specification Section 16.3.1.3.1.1</a>
  </li>
  
</ul>  

      
          
    <p>If Length is zero, this pattern will match all tags regardless of MB, pointer, mask and data.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2TargetTag : public CParameter
{
  public:
    CC1G2TargetTag (void);
    ~CC1G2TargetTag (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u1_t m_Match;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMatch;
//@}

    /** @brief Get accessor functions for the LLRP Match field */
    inline llrp_u1_t
    getMatch (void)
    {
        return m_Match;
    }

    /** @brief Set accessor functions for the LLRP Match field */
    inline void
    setMatch (
      llrp_u1_t value)
    {
        m_Match = value;
    }


  
  
  
  protected:
    llrp_u16_t m_Pointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPointer;
//@}

    /** @brief Get accessor functions for the LLRP Pointer field */
    inline llrp_u16_t
    getPointer (void)
    {
        return m_Pointer;
    }

    /** @brief Set accessor functions for the LLRP Pointer field */
    inline void
    setPointer (
      llrp_u16_t value)
    {
        m_Pointer = value;
    }


  
  
  
  protected:
    llrp_u1v_t m_TagMask;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagMask;
//@}

    /** @brief Get accessor functions for the LLRP TagMask field */
    inline llrp_u1v_t
    getTagMask (void)
    {
        return m_TagMask;
    }

    /** @brief Set accessor functions for the LLRP TagMask field */
    inline void
    setTagMask (
      llrp_u1v_t value)
    {
        m_TagMask = value;
    }


  
  
  
  protected:
    llrp_u1v_t m_TagData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdTagData;
//@}

    /** @brief Get accessor functions for the LLRP TagData field */
    inline llrp_u1v_t
    getTagData (void)
    {
        return m_TagData;
    }

    /** @brief Set accessor functions for the LLRP TagData field */
    inline void
    setTagData (
      llrp_u1v_t value)
    {
        m_TagData = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2Read for LLRP parameter C1G2Read
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=107&view=fit>LLRP Specification Section 15.2.1.3.2.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=157&view=fit>LLRP Specification Section 16.3.1.3.2.1</a>
  </li>
  
</ul>  

      
          
    <p>MB is the memory bank to use. WordPtr is the starting word address. WordCount is the number of 16-bit words to be read. Following is text reproduced from the C1G2 specification regarding WordCount=0. [If WordCount = 0, the tag backscatters the contents of the chosen memory bank starting at WordPtr and ending at the end of the bank, unless MB = 1, in which case the Tag shall backscatter the EPC memory contents starting at WordPtr and ending at the length of the EPC specified by the first 5 bits of the PC if WordPtr lies within the EPC, and shall backscatter the EPC memory contents starting at WordPtr and ending at the end of EPC memory if WordPtr lies outside the EPC.]</p> 
 
          
    <p>Access Password is the password used by the Reader to transition the tag to the secure state so that it can read protected tag memory regions. For example, the Tag's Reserved memory is locked but not permalocked, meaning that the Reader must issue the access password and transition the Tag to the secured state before performing the read operation.  </p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2Read : public CParameter
{
  public:
    CC1G2Read (void);
    ~CC1G2Read (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_AccessPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessPassword;
//@}

    /** @brief Get accessor functions for the LLRP AccessPassword field */
    inline llrp_u32_t
    getAccessPassword (void)
    {
        return m_AccessPassword;
    }

    /** @brief Set accessor functions for the LLRP AccessPassword field */
    inline void
    setAccessPassword (
      llrp_u32_t value)
    {
        m_AccessPassword = value;
    }


  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordPointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordPointer;
//@}

    /** @brief Get accessor functions for the LLRP WordPointer field */
    inline llrp_u16_t
    getWordPointer (void)
    {
        return m_WordPointer;
    }

    /** @brief Set accessor functions for the LLRP WordPointer field */
    inline void
    setWordPointer (
      llrp_u16_t value)
    {
        m_WordPointer = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordCount;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordCount;
//@}

    /** @brief Get accessor functions for the LLRP WordCount field */
    inline llrp_u16_t
    getWordCount (void)
    {
        return m_WordCount;
    }

    /** @brief Set accessor functions for the LLRP WordCount field */
    inline void
    setWordCount (
      llrp_u16_t value)
    {
        m_WordCount = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2Write for LLRP parameter C1G2Write
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=107&view=fit>LLRP Specification Section 15.2.1.3.2.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=157&view=fit>LLRP Specification Section 16.3.1.3.2.2</a>
  </li>
  
</ul>  

      
          
    <p>MB is the memory bank to use. WordPtr is the starting word address. Write Data is the data to be written to the tag. Word Count is the number of words to be written. Depending on the word count, the Reader may have to execute multiple C1G2 air protocol Write commands. Access Password is the password used by the Reader to transition the tag to the secure state so that it can write to protected tag memory regions.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2Write : public CParameter
{
  public:
    CC1G2Write (void);
    ~CC1G2Write (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_AccessPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessPassword;
//@}

    /** @brief Get accessor functions for the LLRP AccessPassword field */
    inline llrp_u32_t
    getAccessPassword (void)
    {
        return m_AccessPassword;
    }

    /** @brief Set accessor functions for the LLRP AccessPassword field */
    inline void
    setAccessPassword (
      llrp_u32_t value)
    {
        m_AccessPassword = value;
    }


  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordPointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordPointer;
//@}

    /** @brief Get accessor functions for the LLRP WordPointer field */
    inline llrp_u16_t
    getWordPointer (void)
    {
        return m_WordPointer;
    }

    /** @brief Set accessor functions for the LLRP WordPointer field */
    inline void
    setWordPointer (
      llrp_u16_t value)
    {
        m_WordPointer = value;
    }


  
  
  
  protected:
    llrp_u16v_t m_WriteData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWriteData;
//@}

    /** @brief Get accessor functions for the LLRP WriteData field */
    inline llrp_u16v_t
    getWriteData (void)
    {
        return m_WriteData;
    }

    /** @brief Set accessor functions for the LLRP WriteData field */
    inline void
    setWriteData (
      llrp_u16v_t value)
    {
        m_WriteData = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2Kill for LLRP parameter C1G2Kill
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=108&view=fit>LLRP Specification Section 15.2.1.3.2.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=157&view=fit>LLRP Specification Section 16.3.1.3.2.3</a>
  </li>
  
</ul>  

      
          
    <p>Kill Password is the value of the kill password to be used or set.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2Kill : public CParameter
{
  public:
    CC1G2Kill (void);
    ~CC1G2Kill (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_KillPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdKillPassword;
//@}

    /** @brief Get accessor functions for the LLRP KillPassword field */
    inline llrp_u32_t
    getKillPassword (void)
    {
        return m_KillPassword;
    }

    /** @brief Set accessor functions for the LLRP KillPassword field */
    inline void
    setKillPassword (
      llrp_u32_t value)
    {
        m_KillPassword = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2Lock for LLRP parameter C1G2Lock
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=108&view=fit>LLRP Specification Section 15.2.1.3.2.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=157&view=fit>LLRP Specification Section 16.3.1.3.2.4</a>
  </li>
  
</ul>  

      
          
    <p>This parameter contains the definition of the access privilege updates (read/write/permalock) to be performed in various locations of the memory. The five data fields for which we can define access control using the lock command are: Kill Password, Access Password, EPC memory, TID memory and User memory. The access privilege updates are expressed as a list of C1G2LockPayload Parameters, one for each memory location.</p> 
 
          
    <p>The Access Password provides the password to enter the secured state.  A Reader can perform a lock operation on a tag only if the tag is in the secured state. The tag enters the secured state only using the Access Password (if a non-zero value).</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CC1G2Lock : public CParameter
{
  public:
    CC1G2Lock (void);
    ~CC1G2Lock (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_AccessPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessPassword;
//@}

    /** @brief Get accessor functions for the LLRP AccessPassword field */
    inline llrp_u32_t
    getAccessPassword (void)
    {
        return m_AccessPassword;
    }

    /** @brief Set accessor functions for the LLRP AccessPassword field */
    inline void
    setAccessPassword (
      llrp_u32_t value)
    {
        m_AccessPassword = value;
    }


  
  
  
  protected:
    std::list<CC1G2LockPayload *> m_listC1G2LockPayload;

  public:
     /** @brief  Returns the first element of the C1G2LockPayload sub-parameter list*/  
    inline std::list<CC1G2LockPayload *>::iterator
    beginC1G2LockPayload (void)
    {
        return m_listC1G2LockPayload.begin();
    }

     /** @brief  Returns the last element of the C1G2LockPayload sub-parameter list*/  
    inline std::list<CC1G2LockPayload *>::iterator
    endC1G2LockPayload (void)
    {
        return m_listC1G2LockPayload.end();
    }

     /** @brief  Clears the LLRP C1G2LockPayload sub-parameter list*/  
    inline void
    clearC1G2LockPayload (void)
    {
        clearSubParameterList ((tListOfParameters *) &m_listC1G2LockPayload);
    }

     /** @brief  Count of the LLRP C1G2LockPayload sub-parameter list*/  
    inline int
    countC1G2LockPayload (void)
    {
        return (int) (m_listC1G2LockPayload.size());
    }

    EResultCode
     /** @brief  Add a C1G2LockPayload to the LLRP sub-parameter list*/  
    addC1G2LockPayload (
      CC1G2LockPayload * pValue);


};


/**
 ** @brief  Class Definition CC1G2LockPayload for LLRP parameter C1G2LockPayload
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=109&view=fit>LLRP Specification Section 15.2.1.3.2.4.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=158&view=fit>LLRP Specification Section 16.3.1.3.2.4.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter contains the definition of the access privilege updates (read/write/permalock) to be performed for a single location of the tag memory. The five data fields for which we can define access control using the lock command are: Kill Password, Access Password, EPC memory, TID memory and User memory.</p> 
  
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2LockPayload : public CParameter
{
  public:
    CC1G2LockPayload (void);
    ~CC1G2LockPayload (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2LockPrivilege m_ePrivilege;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPrivilege;
//@}

    /** @brief Get accessor functions for the LLRP Privilege field */
    inline EC1G2LockPrivilege
    getPrivilege (void)
    {
        return m_ePrivilege;
    }

    /** @brief Set accessor functions for the LLRP Privilege field */
    inline void
    setPrivilege (
      EC1G2LockPrivilege value)
    {
        m_ePrivilege = value;
    }


  
  
  
  protected:
    EC1G2LockDataField m_eDataField;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdDataField;
//@}

    /** @brief Get accessor functions for the LLRP DataField field */
    inline EC1G2LockDataField
    getDataField (void)
    {
        return m_eDataField;
    }

    /** @brief Set accessor functions for the LLRP DataField field */
    inline void
    setDataField (
      EC1G2LockDataField value)
    {
        m_eDataField = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2BlockErase for LLRP parameter C1G2BlockErase
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=109&view=fit>LLRP Specification Section 15.2.1.3.2.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=158&view=fit>LLRP Specification Section 16.3.1.3.2.5</a>
  </li>
  
</ul>  

      
          
    <p>MB is the memory bank to use. WordPtr is the starting word address. Word Count is the number of 16-bit words to be read. Access Password is the password used by the Reader to transition the tag to the secure state so that it can erase protected tag memory regions.</p> 
 
          
    <p>Readers that do not support C1G2BlockErase 
   <b>SHALL</b>
  set CanSupportBlockErase to false in C1G2LLRPCapabilities. If such a Reader receives an ADD_ACCESSSPEC with an AccessSpec that contained this OpSpec parameter, the Reader 
   <b>SHALL</b>
  return an error for that message and not add the AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2BlockErase : public CParameter
{
  public:
    CC1G2BlockErase (void);
    ~CC1G2BlockErase (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_AccessPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessPassword;
//@}

    /** @brief Get accessor functions for the LLRP AccessPassword field */
    inline llrp_u32_t
    getAccessPassword (void)
    {
        return m_AccessPassword;
    }

    /** @brief Set accessor functions for the LLRP AccessPassword field */
    inline void
    setAccessPassword (
      llrp_u32_t value)
    {
        m_AccessPassword = value;
    }


  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordPointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordPointer;
//@}

    /** @brief Get accessor functions for the LLRP WordPointer field */
    inline llrp_u16_t
    getWordPointer (void)
    {
        return m_WordPointer;
    }

    /** @brief Set accessor functions for the LLRP WordPointer field */
    inline void
    setWordPointer (
      llrp_u16_t value)
    {
        m_WordPointer = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordCount;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordCount;
//@}

    /** @brief Get accessor functions for the LLRP WordCount field */
    inline llrp_u16_t
    getWordCount (void)
    {
        return m_WordCount;
    }

    /** @brief Set accessor functions for the LLRP WordCount field */
    inline void
    setWordCount (
      llrp_u16_t value)
    {
        m_WordCount = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2BlockWrite for LLRP parameter C1G2BlockWrite
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=110&view=fit>LLRP Specification Section 15.2.1.3.2.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=158&view=fit>LLRP Specification Section 16.3.1.3.2.6</a>
  </li>
  
</ul>  

      
          
    <p>MB is the memory bank to use. WordPtr is the starting word address. Word Count is the number of 16-bit words to be written. Depending on the word count, the Reader may have to execute multiple C1G2 air protocol block write commands. Write Data is the data to be written to the tag. Access Password is the password used by the Reader to transition the tag to the secure state so that it can write to protected tag memory regions.</p> 
 
          
    <p>Readers that do not support C1G2BlockWrite 
   <b>SHALL</b>
  set CanSupportBlockWrite to false in C1G2LLRPCapabilities. If such a Reader receives an ADD_ACCESSSPEC with an AccessSpec that contained this OpSpec parameter, the Reader 
   <b>SHALL</b>
  return an error for that message and not add the AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
    
    
    
  
 **/

  
  
  
class CC1G2BlockWrite : public CParameter
{
  public:
    CC1G2BlockWrite (void);
    ~CC1G2BlockWrite (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u32_t m_AccessPassword;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdAccessPassword;
//@}

    /** @brief Get accessor functions for the LLRP AccessPassword field */
    inline llrp_u32_t
    getAccessPassword (void)
    {
        return m_AccessPassword;
    }

    /** @brief Set accessor functions for the LLRP AccessPassword field */
    inline void
    setAccessPassword (
      llrp_u32_t value)
    {
        m_AccessPassword = value;
    }


  
  
  
  protected:
    llrp_u2_t m_MB;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdMB;
//@}

    /** @brief Get accessor functions for the LLRP MB field */
    inline llrp_u2_t
    getMB (void)
    {
        return m_MB;
    }

    /** @brief Set accessor functions for the LLRP MB field */
    inline void
    setMB (
      llrp_u2_t value)
    {
        m_MB = value;
    }


  
  
  
  protected:
    llrp_u16_t m_WordPointer;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWordPointer;
//@}

    /** @brief Get accessor functions for the LLRP WordPointer field */
    inline llrp_u16_t
    getWordPointer (void)
    {
        return m_WordPointer;
    }

    /** @brief Set accessor functions for the LLRP WordPointer field */
    inline void
    setWordPointer (
      llrp_u16_t value)
    {
        m_WordPointer = value;
    }


  
  
  
  protected:
    llrp_u16v_t m_WriteData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdWriteData;
//@}

    /** @brief Get accessor functions for the LLRP WriteData field */
    inline llrp_u16v_t
    getWriteData (void)
    {
        return m_WriteData;
    }

    /** @brief Set accessor functions for the LLRP WriteData field */
    inline void
    setWriteData (
      llrp_u16v_t value)
    {
        m_WriteData = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2EPCMemorySelector for LLRP parameter C1G2EPCMemorySelector
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=110&view=fit>LLRP Specification Section 15.2.1.5.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=159&view=fit>LLRP Specification Section 16.3.1.5.1</a>
  </li>
  
</ul>  

      
          
    <p>This parameter is used to determine what contents are of interest in the C1G2EPC memory bank for reporting. If enableCRC and enablePC is set to false, only the EPC is returned in the RO Report. If enablePC is set to true, the PC bits and the EPC are returned in the RO Report. If enablePC and enableCRC is set to true, the EPC, PC bits and CRC are returned in the RO Report.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CC1G2EPCMemorySelector : public CParameter
{
  public:
    CC1G2EPCMemorySelector (void);
    ~CC1G2EPCMemorySelector (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u1_t m_EnableCRC;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnableCRC;
//@}

    /** @brief Get accessor functions for the LLRP EnableCRC field */
    inline llrp_u1_t
    getEnableCRC (void)
    {
        return m_EnableCRC;
    }

    /** @brief Set accessor functions for the LLRP EnableCRC field */
    inline void
    setEnableCRC (
      llrp_u1_t value)
    {
        m_EnableCRC = value;
    }


  
  
  
  protected:
    llrp_u1_t m_EnablePCBits;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdEnablePCBits;
//@}

    /** @brief Get accessor functions for the LLRP EnablePCBits field */
    inline llrp_u1_t
    getEnablePCBits (void)
    {
        return m_EnablePCBits;
    }

    /** @brief Set accessor functions for the LLRP EnablePCBits field */
    inline void
    setEnablePCBits (
      llrp_u1_t value)
    {
        m_EnablePCBits = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2_PC for LLRP parameter C1G2_PC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=111&view=fit>LLRP Specification Section 15.2.1.5.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=159&view=fit>LLRP Specification Section 16.3.1.5.2</a>
  </li>
  
</ul>  

      
          
    <p>Protocol control bits from the UHF Gen2 Air Interface protocol</p> 
 
       
  <HR>

    
    
  
 **/

  
  
  
class CC1G2_PC : public CParameter
{
  public:
    CC1G2_PC (void);
    ~CC1G2_PC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_PC_Bits;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdPC_Bits;
//@}

    /** @brief Get accessor functions for the LLRP PC_Bits field */
    inline llrp_u16_t
    getPC_Bits (void)
    {
        return m_PC_Bits;
    }

    /** @brief Set accessor functions for the LLRP PC_Bits field */
    inline void
    setPC_Bits (
      llrp_u16_t value)
    {
        m_PC_Bits = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2_CRC for LLRP parameter C1G2_CRC
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=111&view=fit>LLRP Specification Section 15.2.1.5.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=159&view=fit>LLRP Specification Section 16.3.1.5.3</a>
  </li>
  
</ul>  

      
              
    <p>CRC generated by the tag from the UHF Gen2 Air Interface Protocol</p> 
 
       
  <HR>

    
    
  
 **/

  
  
  
class CC1G2_CRC : public CParameter
{
  public:
    CC1G2_CRC (void);
    ~CC1G2_CRC (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_CRC;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdCRC;
//@}

    /** @brief Get accessor functions for the LLRP CRC field */
    inline llrp_u16_t
    getCRC (void)
    {
        return m_CRC;
    }

    /** @brief Set accessor functions for the LLRP CRC field */
    inline void
    setCRC (
      llrp_u16_t value)
    {
        m_CRC = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2SingulationDetails for LLRP parameter C1G2SingulationDetails
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=111&view=fit>LLRP Specification Section 15.2.1.5.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=159&view=fit>LLRP Specification Section 16.3.1.5.4</a>
  </li>
  
</ul>  

    
    
    
  
 **/

  
  
  
class CC1G2SingulationDetails : public CParameter
{
  public:
    CC1G2SingulationDetails (void);
    ~CC1G2SingulationDetails (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    llrp_u16_t m_NumCollisionSlots;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumCollisionSlots;
//@}

    /** @brief Get accessor functions for the LLRP NumCollisionSlots field */
    inline llrp_u16_t
    getNumCollisionSlots (void)
    {
        return m_NumCollisionSlots;
    }

    /** @brief Set accessor functions for the LLRP NumCollisionSlots field */
    inline void
    setNumCollisionSlots (
      llrp_u16_t value)
    {
        m_NumCollisionSlots = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumEmptySlots;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumEmptySlots;
//@}

    /** @brief Get accessor functions for the LLRP NumEmptySlots field */
    inline llrp_u16_t
    getNumEmptySlots (void)
    {
        return m_NumEmptySlots;
    }

    /** @brief Set accessor functions for the LLRP NumEmptySlots field */
    inline void
    setNumEmptySlots (
      llrp_u16_t value)
    {
        m_NumEmptySlots = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2ReadOpSpecResult for LLRP parameter C1G2ReadOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=111&view=fit>LLRP Specification Section 15.2.1.5.5.1</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=159&view=fit>LLRP Specification Section 16.3.1.5.5.1</a>
  </li>
  
</ul>  

      
          
    <p>Contains the results from a read operation.</p> 
 
       
  <HR>

    
    
    
    
  
 **/

  
  
  
class CC1G2ReadOpSpecResult : public CParameter
{
  public:
    CC1G2ReadOpSpecResult (void);
    ~CC1G2ReadOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2ReadResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2ReadResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2ReadResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u16v_t m_ReadData;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdReadData;
//@}

    /** @brief Get accessor functions for the LLRP ReadData field */
    inline llrp_u16v_t
    getReadData (void)
    {
        return m_ReadData;
    }

    /** @brief Set accessor functions for the LLRP ReadData field */
    inline void
    setReadData (
      llrp_u16v_t value)
    {
        m_ReadData = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2WriteOpSpecResult for LLRP parameter C1G2WriteOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=112&view=fit>LLRP Specification Section 15.2.1.5.5.2</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=160&view=fit>LLRP Specification Section 16.3.1.5.5.2</a>
  </li>
  
</ul>  

      
          
    <p>Contains the result from a write operation.</p> 
 
          
    <p>If the number of words written is not equal to the length of the data pattern to write, the Result  
   <b>SHALL</b>
  be non-zero.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CC1G2WriteOpSpecResult : public CParameter
{
  public:
    CC1G2WriteOpSpecResult (void);
    ~CC1G2WriteOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2WriteResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2WriteResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2WriteResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumWordsWritten;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumWordsWritten;
//@}

    /** @brief Get accessor functions for the LLRP NumWordsWritten field */
    inline llrp_u16_t
    getNumWordsWritten (void)
    {
        return m_NumWordsWritten;
    }

    /** @brief Set accessor functions for the LLRP NumWordsWritten field */
    inline void
    setNumWordsWritten (
      llrp_u16_t value)
    {
        m_NumWordsWritten = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2KillOpSpecResult for LLRP parameter C1G2KillOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=112&view=fit>LLRP Specification Section 15.2.1.5.5.3</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=160&view=fit>LLRP Specification Section 16.3.1.5.5.3</a>
  </li>
  
</ul>  

      
          Contains the result from a kill operation.
       
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2KillOpSpecResult : public CParameter
{
  public:
    CC1G2KillOpSpecResult (void);
    ~CC1G2KillOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2KillResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2KillResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2KillResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2LockOpSpecResult for LLRP parameter C1G2LockOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.4</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=160&view=fit>LLRP Specification Section 16.3.1.5.5.4</a>
  </li>
  
</ul>  

      
          
    <p>Contains the result of a lock operation.</p> 
 
       
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2LockOpSpecResult : public CParameter
{
  public:
    CC1G2LockOpSpecResult (void);
    ~CC1G2LockOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2LockResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2LockResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2LockResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2BlockEraseOpSpecResult for LLRP parameter C1G2BlockEraseOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.5</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=160&view=fit>LLRP Specification Section 16.3.1.5.5.5</a>
  </li>
  
</ul>  

      
          
    <p>Contains the result of a block erase operation.</p> 
 
          
    <p>Readers that do not support C1G2 Block Erase 
   <b>SHALL</b>
  set CanSupportBlockErase to false in C1G2LLRPCapabilities. If such a Reader receives an ADD_ACCESSSPEC with an AccessSpec that contains this OpSpec parameter, the Reader 
   <b>SHALL</b>
  return an error for that message and not add the AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
  
 **/

  
  
  
class CC1G2BlockEraseOpSpecResult : public CParameter
{
  public:
    CC1G2BlockEraseOpSpecResult (void);
    ~CC1G2BlockEraseOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2BlockEraseResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2BlockEraseResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2BlockEraseResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
};


/**
 ** @brief  Class Definition CC1G2BlockWriteOpSpecResult for LLRP parameter C1G2BlockWriteOpSpecResult
 **
 
    
      
<ul>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=113&view=fit>LLRP Specification Section 15.2.1.5.5.6</a>
  </li>
    
    <li><b>Document Reference</b>  
   <a href=http://www.epcglobalinc.org/standards/llrp/llrp_1_0_1-standard-20070813.pdf#page=161&view=fit>LLRP Specification Section 16.3.1.5.5.6</a>
  </li>
  
</ul>  

      
          
    <p>Contains the result of a block write operation</p> 
 
          
    <p>Readers that do not support C1G2 Block Write 
   <b>SHALL</b>
  set CanSupportBlockWrite to false in C1G2LLRPCapabilities. If such a Reader receives an ADD_ACCESSSPEC with an AccessSpec that contains this OpSpec parameter, the Reader 
   <b>SHALL</b>
  return an error for that message and not add the AccessSpec.</p> 
 
      <SMALL><i>Copyright 2006, 2007, EPCglobal Inc. The proprietary text of EPCglobal Inc. included here is in not a Contribution to the LLRP toolkit, under Apache License, Version 2.0. The right to use the proprietary text is limited to reproduction and display thereof within the work.</i></SMALL> 
  <HR>

    
    
    
    
  
 **/

  
  
  
class CC1G2BlockWriteOpSpecResult : public CParameter
{
  public:
    CC1G2BlockWriteOpSpecResult (void);
    ~CC1G2BlockWriteOpSpecResult (void);

/** @name Internal Framework Functions */
//@{

    static const CFieldDescriptor * const
    s_apFieldDescriptorTable[];

    static const CTypeDescriptor
    s_typeDescriptor;

    void
    decodeFields (
      CDecoderStream *          pDecoderStream);

    void
    assimilateSubParameters (
      CErrorDetails *           pError);

    void
    encode (
      CEncoderStream *          pEncoderStream) const;

  

    static CElement *
    s_construct (void);

    static void
    s_decodeFields (
      CDecoderStream *          pDecoderStream,
      CElement *                pElement);
//@}

  
  
  
  
  protected:
    EC1G2BlockWriteResultType m_eResult;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdResult;
//@}

    /** @brief Get accessor functions for the LLRP Result field */
    inline EC1G2BlockWriteResultType
    getResult (void)
    {
        return m_eResult;
    }

    /** @brief Set accessor functions for the LLRP Result field */
    inline void
    setResult (
      EC1G2BlockWriteResultType value)
    {
        m_eResult = value;
    }


  
  
  
  protected:
    llrp_u16_t m_OpSpecID;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdOpSpecID;
//@}

    /** @brief Get accessor functions for the LLRP OpSpecID field */
    inline llrp_u16_t
    getOpSpecID (void)
    {
        return m_OpSpecID;
    }

    /** @brief Set accessor functions for the LLRP OpSpecID field */
    inline void
    setOpSpecID (
      llrp_u16_t value)
    {
        m_OpSpecID = value;
    }


  
  
  
  protected:
    llrp_u16_t m_NumWordsWritten;

/** @name Internal Framework Functions */
//@{
  public:
    static const CFieldDescriptor
    s_fdNumWordsWritten;
//@}

    /** @brief Get accessor functions for the LLRP NumWordsWritten field */
    inline llrp_u16_t
    getNumWordsWritten (void)
    {
        return m_NumWordsWritten;
    }

    /** @brief Set accessor functions for the LLRP NumWordsWritten field */
    inline void
    setNumWordsWritten (
      llrp_u16_t value)
    {
        m_NumWordsWritten = value;
    }


  
};


/*@}*/ 

class CSpecParameter
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAccessCommandOpSpec
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAccessCommandOpSpecResult
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CEPCParameter
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CTimestamp
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolLLRPCapabilities
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolUHFRFModeTable
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolInventoryCommandSettings
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolTagSpec
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolEPCMemorySelector
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolTagData
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};

class CAirProtocolSingulationDetails
{
/** @name Internal Framework Functions */
//@{
  public:
    static const CTypeDescriptor
    s_typeDescriptor;

    static llrp_bool_t
    isMember (
      CParameter *              pParameter);
//@}

};


/** @brief Enrolls the types for Core into the LTKCPP registry
 ** 
 ** LTKCPP needs an internal registry for storing all the type information.  This function
 ** is required to enroll the types for the Core into
 ** the operating registry.  
 ** 
 ** For example -- in order to decode and encode packets from the core LLRP specification
 ** The user must EnrollCoreTypesIntoRegistry.
 **
 ** @ingroup LTKCoreElement
 */
extern void
enrollCoreTypesIntoRegistry (
  CTypeRegistry *               pTypeRegistry);
