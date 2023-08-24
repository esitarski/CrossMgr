import os

class UserNotFound(Exception):
    pass

### Windows ###
if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes

    class WinError:     # [1]
        InvalidParameter = 87
        InvalidSid = 1337

    class NtStatus:     # [2]
        Success         = 0x00000000
        NoneMapped      = 0xC0000073

    class AccessMask:   # [3]
        Delete                      = 0x00010000
        ReadControl                 = 0x00020000
        WriteDAC                    = 0x00040000
        WriteOwner                  = 0x00080000
        Synchronize                 = 0x00100000
        StandardRightsRequired      = 0x000F0000
        StandardRightsRead          = ReadControl
        StandardRightsWrite         = ReadControl
        StandardRightsExecute       = ReadControl
        StandardRightsAll           = 0x001F0000
        SpecificRightsAll           = 0x0000FFFF

    class TokenAccessLevels:        # See [4] and TokenAccessLevels.cs in Mono source
        AssignPrimary       = 1<<0
        Duplicate           = 1<<1
        Impersonate         = 1<<2
        Query               = 1<<3
        QuerySource         = 1<<4
        AdjustPrivileges    = 1<<5
        AdjustGroups        = 1<<6
        AdjustDefault       = 1<<7
        AdjustSessionId     = 1<<8
        Read                = AccessMask.StandardRightsRead | Query
        Write               = AccessMask.StandardRightsWrite | AdjustPrivileges | AdjustGroups | AdjustDefault
        AllAccess           = AccessMask.StandardRightsRequired | 0x1FF
        MaximumAllowed      = 0x2000000

    class TokenInformationClass:    # [5]
        User,\
        Groups,\
        Privileges,\
        Owner,\
        PrimaryGroup,\
        DefaultDacl,\
        Source,\
        Type,\
        ImpersonationLevel,\
        Statistics,\
        RestrictedSids,\
        SessionId,\
        GroupsAndPrivileges,\
        SessionReference,\
        SandBoxInert,\
        AuditPolicy,\
        Origin,\
        ElevationType,\
        LinkedToken,\
        Elevation,\
        HasRestrictions,\
        AccessInformation,\
        VirtualizationAllowed,\
        VirtualizationEnabled,\
        IntegrityLevel,\
        UIAccess,\
        MandatoryPolicy,\
        LogonSid,\
        IsAppContainer,\
        Capabilities,\
        AppContainerSid,\
        AppContainerNumber,\
        UserClaimAttributes,\
        DeviceClaimAttributes,\
        RestrictedUserClaimAttributes,\
        RestrictedDeviceClaimAttributes,\
        DeviceGroups,\
        RestrictedDeviceGroups,\
        SecurityAttributes,\
        IsRestricted,\
        = range(1, 41)

    class SidNameUse:   # [6]
        TypeUser,\
        TypeGroup,\
        TypeDomain,\
        TypeAlias,\
        TypeWellKnownGroup,\
        TypeDeletedAccount,\
        TypeInvalid,\
        TypeUnknown,\
        TypeComputer,\
        TypeLabel,\
        = range(1, 11)

    # Type declarations
    pSID = wintypes.HANDLE
    ENUM = ctypes.c_uint
 
    class SidAndAttributes(ctypes.Structure):   # [7]
        _fields_ = (
            ('Sid', pSID),
            ('Attributes', wintypes.DWORD),
        )

    class TokenUser(ctypes.Structure):          # [8]
        _fields_ = (
            ('User', SidAndAttributes),
        )

    _GetCurrentProcess = windll.kernel32.GetCurrentProcess      # [9]
    _GetCurrentProcess.restype = wintypes.HANDLE

    _OpenProcessToken = windll.advapi32.OpenProcessToken        # [10]
    _OpenProcessToken.restype = wintypes.BOOL
    _OpenProcessToken.argtypes = (
        wintypes.HANDLE,                # ProcessHandle
        wintypes.DWORD,                 # DesiredAccess
        ctypes.POINTER(wintypes.HANDLE) # TokenHandle (out)
    )

    _GetTokenInformation = windll.advapi32.GetTokenInformation  # [11]
    _GetTokenInformation.restype = wintypes.BOOL
    _GetTokenInformation.argtypes = (
        wintypes.HANDLE,    # TokenHandle
        ENUM,               # TokenInformationClass
        ctypes.c_void_p,    # TokenInformation (out)
        wintypes.DWORD,     # TokenInformationLength
        wintypes.PDWORD     # ReturnLength (out)
    )

    _ConvertStringSidToSid = windll.advapi32.ConvertStringSidToSidW     # [12]
    _ConvertStringSidToSid.restype = wintypes.BOOL
    _ConvertStringSidToSid.argtypes = (
        wintypes.LPWSTR,        # StringSid
        ctypes.POINTER(pSID),   # Sid (out)
    )

    _CovertSidToStringSid = windll.advapi32.ConvertSidToStringSidW      # [13]
    _CovertSidToStringSid.restype = wintypes.BOOL
    _CovertSidToStringSid.argtypes = (
        pSID,                           # Sid
        ctypes.POINTER(wintypes.LPWSTR) # StringSid (out)
    )

    _LocalFree = windll.kernel32.LocalFree      # [14]
    _LocalFree.restype = None
    _LocalFree.argtypes = (wintypes.HANDLE,)

    _IsValidSid = windll.advapi32.IsValidSid    # [15]
    _IsValidSid.restype = wintypes.BOOL
    _IsValidSid.argtypes = (pSID,)

    _LookupAccountSid = windll.advapi32.LookupAccountSidW   # [16]
    _LookupAccountSid.restype = wintypes.BOOL
    _LookupAccountSid.argtypes = (
        wintypes.LPWSTR,        # lpSystemName (optional)
        pSID,                   # lpSid
        wintypes.LPWSTR,        # lpName (out, optional)
        wintypes.LPDWORD,       # cchName (in/out)
        wintypes.LPWSTR,        # lpReferencedDomainName (out, optional)
        wintypes.LPDWORD,       # cchReferencedDomainName (in/out)
        ctypes.POINTER(ENUM),   # peUse (out)
    )

    class Sid:
        def __init__(self, sid):
            if isinstance(sid, str):
                self.pointer = pSID()
                status = _ConvertStringSidToSid(sid, self.pointer)
                if status == WinError.InvalidSid:
                    raise ValueError('Not a valid sid: %s' % sid)
                elif not status:
                    raise ctypes.WinError()
            else:
                if not _IsValidSid(sid):
                    raise ValueError('Invalid sid: %s' % sid)
                self.pointer = sid

        def __str__(self):
            buf = wintypes.LPWSTR()
            if not _CovertSidToStringSid(self.pointer, buf):
                raise ctypes.WinError()
            string_sid = buf.value
            _LocalFree(buf)
            return string_sid

    def _getpsid():
        proc_token = wintypes.HANDLE()
        if not _OpenProcessToken(_GetCurrentProcess(), TokenAccessLevels.Read, proc_token):
            raise ctypes.WinError()

        # Get required length by calling with a 0 length buffer
        length = wintypes.DWORD()
        _GetTokenInformation(proc_token, TokenInformationClass.User, None, 0, length)

        buf = ctypes.create_string_buffer(length.value)
        if not _GetTokenInformation(proc_token, TokenInformationClass.User, buf, len(buf), length):
            raise ctypes.WinError()

        token_user = ctypes.cast(buf, ctypes.POINTER(TokenUser)).contents
        return token_user.User.Sid


    def getuid():
        return str(Sid(_getpsid()))

    def lookup_username(uid=None):
        sid = Sid(uid or _getpsid())

        use = ENUM()
        cchName = wintypes.DWORD()
        cchReferencedDomainName = wintypes.DWORD()

        # Get required lengths by calling with 0 length buffers
        _LookupAccountSid(None, sid.pointer, None, cchName, None, cchReferencedDomainName, use)

        name = ctypes.create_unicode_buffer(cchName.value)
        domain = ctypes.create_unicode_buffer(cchReferencedDomainName.value)

        status = _LookupAccountSid(None, sid.pointer, name, cchName, domain, cchReferencedDomainName, use)
        if status == NtStatus.NoneMapped:
            raise UserNotFound('No such sid: %s' % sid)
        elif not status:
            raise ctypes.WinError()

        if use.value != SidNameUse.TypeUser:
            raise ValueError('Not a user sid: %s' % sid)

        return name.value

### Posix ###
else:
    import pwd
    from os import getuid

    def lookup_username(uid=None):
        if uid is None:
            uid = getuid()
        try:
            return pwd.getpwuid(uid)[0]
        except (KeyError, TypeError):
            raise UserNotFound('No such uid: %s' % uid)


if __name__ == '__main__':
    print('%s %s' % (getuid(), lookup_username()))

