# *****************************************************************************
# * Copyright by ams OSRAM AG                                                 *
# * All rights are reserved.                                                  *
# *                                                                           *
# *FOR FULL LICENSE TEXT SEE LICENSES-MIT.TXT                                 *
# *****************************************************************************
"""
The Register Page converter. See below for a usage example.
"""
import ctypes
import copy

class RegisterPageConverter:

    @staticmethod
    def generateDict( reg_page ):
        """Generate a dictionary for the specified register-page and return it and the base-address and the last-address 
        Args:
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
            dictionary, base-addr, last-addr 
        """
        _dict = {}
        _base_addr = 0xFFFFFFFF
        _last_addr = 0
        # first find the base address of the page
        for _v in vars(reg_page):
            _reg = getattr(reg_page,_v)
            _addr = getattr(_reg, "addr")
            for _name, _t, _bits in _reg._fields_:
                _dict[_name] = 0
            if _addr < _base_addr:
                _base_addr = _addr
            if _last_addr < _addr:
                _last_addr = _addr
        return _dict, _base_addr, _last_addr

    @staticmethod
    def regByAddr(reg_page,addr):
        """Find the register with the given addr in the page
        Args:
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
            addr: the address for that a register is requested
        Returns:
            the register object for the given address, None if there is no register at the given address
        """
        for _v in vars(reg_page):
            _reg = getattr(reg_page,_v)
            if getattr(_reg,"addr") == addr:
                return _reg
        return None                         # if there is a hole in the reg-map 

    @staticmethod
    def getFieldValueByName(reg_page,field_name):
        """Find the field in the registers with the given name
        Args:
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
            field_name: the name of the field in one of the registers
        Returns:
            the value of the field (raises an exception of the field does not exist)
        """
        for _v in vars(reg_page):
            _reg = getattr(reg_page,_v)
            for (_name,_,_) in _reg._fields_:
                if _name == field_name:
                    return getattr( _reg, _name )
        raise Exception( "getFieldValueByName: No field with name {} exists".format(field_name))

    @staticmethod
    def setFieldValueByName(reg_page,field_name,value):
        """Find the field in the registers with the given name and set the value
        Args:
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
            field_name: the name of the field in one of the registers
            value: the value to that the field shall be set (no range check is done here, value is trucated automatically)
        (raises an exception of the field does not exist)
        """
        for _v in vars(reg_page):
            _reg = getattr(reg_page,_v)
            for (_name,_,_) in _reg._fields_:
                if _name == field_name:
                    setattr( _reg, _name, value )
                    return
        raise Exception( "setFieldValueByName No field with name {} exists".format(field_name))

    @staticmethod
    def fillDict( b_page, reg_page ):
        """Fill the given bytestream into the dictionary corresponding to given page 
        Args:
            b_page: a bytestream that shall be filled into the registers and ends up in the dictionary that
            represents the reg_page
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
            dictionary representing the corresponding register page
        """
        _dict, _base_addr, _last_addr = RegisterPageConverter.generateDict( reg_page )
        _b = list(b_page)
        if _last_addr+1-_base_addr < len(_b):
            print( "WARNING: number of bytes is more than the given register page has, cutting data off")
            _b = _b[0:_last_addr+1]
        assert len(_b) <= _last_addr+1-_base_addr, "ERROR internal program error"
        # now do a byte fill of the registers each is 8-bits 
        for _addr in range(_base_addr, _base_addr+len(_b)):
            _reg = RegisterPageConverter.regByAddr(reg_page, _addr)
            if _reg:                # else this is a hole in the reg-map
                _dst = ctypes.byref(_reg)
                _src = bytes(_b[_addr-_base_addr:_addr-_base_addr+1])
                ctypes.memmove(_dst, _src, 1)        # only 8-bit registers are supported here
            else:
                #print( "fillDict: No reg at addr {} omitting".format(_addr))
                pass
        # now copy bit-fields values to the dictionary
        for _key in _dict:
            _dict[_key] = RegisterPageConverter.getFieldValueByName(reg_page, _key)
        return _dict

    @staticmethod
    def fillPage( d_page, reg_page ):
        """Fill the given dictionary into a bytestream for given page (holes are filled with 0) 
        Args:
            d_page: dictionary representing the corresponding register page
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
            a bytestream that represents the registers values are taken from the dictionary
        """
        _page = []
        _, _base_addr, _last_addr = RegisterPageConverter.generateDict( reg_page ) # just want to have first and last reg addr
        _b = [0]*(_last_addr-_base_addr+1)          # make an array of 0 and fill in the values later
        # now copy bit-fields values from the the dictionary to the reg_page
        for _key, _value in d_page.items():
            RegisterPageConverter.setFieldValueByName(reg_page,_key,_value)             
        # now convert the register page to a bytearray
        for _addr in range(_base_addr, _base_addr+len(_b)):
            _reg = RegisterPageConverter.regByAddr(reg_page, _addr)
            if _reg:
                _value = int.from_bytes(bytearray(_reg),byteorder='little',signed=False)
            else:                               # no register at this location, write a 0
                #print( "fillPage: No reg at addr {}, set to 0".format(_addr))
                _value = 0
            _page.append( _value )
        return bytearray(_page)

    @staticmethod
    def _baseName( name ):
        """Function makes some assumptions about what is the base-name of a field (by stripping away trailing _ and numbers)
        Returns
            base-name 
        """
        _name_list = name.split('_')
        _remove = ""
        for _sub in reversed(_name_list):
            if _sub.isnumeric():
                _remove = "_" + _sub + _remove          # remove trailing numbers (probably bit-indices)
            else:
                if _sub == "MSB" or _sub == "LSB":
                    _remove = "_" + _sub + _remove      # if MSB or LSB is used, break here, no more looking for numbers
                break
        _new = name.replace( _remove, "" )
        return _new        

    @staticmethod
    def _combinedFieldsDict( reg_page ):
        """Generate a dictionary with possible combined names. The key is the basename the value 
           is the list of original names
        Args:
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Return:
            dictionary of possible combined names with original names
        """
        _d, _ , _ = RegisterPageConverter.generateDict( reg_page ) # just want to have first and last reg addr
        _combine = {}
        # get a dictionary of base-names
        for _k in _d:
            _base_name = RegisterPageConverter._baseName( _k )
            if _base_name in _combine:
                _combine[_base_name] = _combine[_base_name] + [ _k ]    # list of original names
            else:
                _combine[_base_name] = [ _k ]
        #print( _combine )
        return _combine

    def _suffixSort( a, reverse ):
        """Sort the array based on the suffix
        Args:
            a: array to be sorted based on the suffix
            reverse: if set to True than the higher numbers (or MSB) come first, else lower numbers (or LSB) come first
        Returns:
            sorted array             
        """
        _b = [[0 for x in range(2)] for y in range(len(a))]
        for _idx, _element in enumerate(a):
            _split = _element.split("_")
            _last = _split[-1]
            if _last.isnumeric():
                _b[_idx][0] = int(_last)        # suffix as a number
                _b[_idx][1] = _element          # original name             
            else:
                if _last == "MSB":
                    _b[_idx][0] = 1             # suffix as a number
                    _b[_idx][1] = _element      # original name             
                elif _last == "LSB":
                    _b[_idx][0] = 0             # suffix as a number
                    _b[_idx][1] = _element      # original name             
                else:
                    raise Exception( "splitSort suffix is not a number and not MSB/LSB {}".format(_last))
        # now _b[0] is an array of numbers that can be sorted. Sort must also be applied to array _b[1]
        _c = sorted(_b, key=lambda x: x[0], reverse=reverse)
        # Use a list comprehension to extract the element at index 'N' from each sub-list
        _d = [i[1] for i in _c]
        return _d                    # return sorted array 

    @staticmethod
    def _combineFields( d_page, reg_page ):
        """Function checks the page for similiar field names and combines them to 1 field
        Args:
            d_page: dictionary representing the corresponding register page
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
           combined dictionary (values are shifted and summed up)
        """
        _d2 = copy.deepcopy(d_page)                 # do not touch the input dictionary, user may get confused
        # get a dictionary of base-names
        _combine = RegisterPageConverter._combinedFieldsDict( reg_page )
        # now reconstruct a dictionary of combined fields only
        _d = {}         
        for _k, _names in _combine.items():
            if len(_names) > 1:                 # there is something to be combined:
                _names = RegisterPageConverter._suffixSort(_names, reverse=True)       # do sort them from MSB to LSB, or 9..0
                _value = 0
                for _kk in _names:
                    _value = _value * 256 + d_page[_kk] # construct bigger value from smaller ones
                    del _d2[_kk]                   # remove this entry from the dictionary 
                _d[_k] = _value
        # now copy over the others where there were no combinations needed
        for _k, _v in _d2.items():
            _d[_k] = _v     
        return _d

    @staticmethod
    def _splitFields( d_page, reg_page ):
        """Function splits names in the combined dictionary into their individual sub-registers
        Args:
            d_page: dictionary representing the corresponding register page
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
            a split-up dictionary where each value is a single byte
        """
        # get a dictionary of base-names
        _split = RegisterPageConverter._combinedFieldsDict( reg_page )
        # now reconstruct a dictionary of split fields only
        _d2 = copy.deepcopy(d_page)                  # do not touch the input dictionary, user may get confused
        _d = {}        
        for _k, _names in _split.items():
            if len(_names) > 1:                 # there is something to be split:
                _names = RegisterPageConverter._suffixSort(_names, reverse=False)  # do sort them from LSB to MSB, 0..9
                _value = _d2[_k]                # combined value needs to be split
                for _k2 in _names:
                    _d[_k2] = _value % 256      # use lower 8-bits only
                    _value = _value // 256      # remove one byte
                del _d2[_k]                     # remove this entry from the dictionary
        # now copy over the others where there were no combinations needed
        for _k, _v in _d2.items():
            _d[_k] = _v     
        return _d

    @staticmethod
    def readPageToDict( b_page, reg_page ):
        """Use this method to read in a register page from a bytestream and generate a combined dictionary
        Args:
            b_page: a bytestream that represents the registers values
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
            dictionary for specified register page (values are filled in from the bytestream)
        """
        _dict = RegisterPageConverter.fillDict( b_page, reg_page )
        _dict = RegisterPageConverter._combineFields( _dict, reg_page ) 
        return _dict

    @staticmethod
    def readDictToPage( d_page, reg_page ):
        """Use this method to split a combined dictionary and generate a page bytestream
        Args:
            d_page: dictionary representing the corresponding register page
            reg_page: a register page that shall be generated with the amsOSRAM RegGen
        Returns:
           bytestream for the specified register page (values are taken from dictionary)
        """
        _dict = RegisterPageConverter._splitFields( d_page, reg_page )
        _page = RegisterPageConverter.fillPage( _dict, reg_page )
        return _page


if __name__ == "__main__":

    def comparePages(b0, b1):
        assert len(b0) == len(b1), "Page differ in len"
        for i in range(len(b0)):
            assert b0[i] == b1[i], "Pages differ in index {}: {} {}".format(i, b0[i], b1[i])

    def compareDicts(d0,d1):
        assert len(d0) == len(d1), "Error dicts differ in len"
        for k in d0:
            assert d0[k] == d1[k], "Values differ d0[{}]={} d1[{}]={}".format(k,d0[k], k,d1[k])


    from tmf8829_config_page import Tmf8829_config_page as Tmf8829ConfigRegs

    # --------- config page --------------------------------------------------------------------

    # an empty bytearray will fill the dictionary with default values from the register definition
    cfgDict0 = RegisterPageConverter.readPageToDict( bytearray(), Tmf8829ConfigRegs() )       

    # convert the dictionary to a bytearray
    cfgBytes0 = RegisterPageConverter.readDictToPage( cfgDict0, Tmf8829ConfigRegs() )        

    # convert the bytearray back to a dictionary
    cfgDict1 = RegisterPageConverter.readPageToDict( cfgBytes0, Tmf8829ConfigRegs() )       

    # for testing purposes we re-convert the 2nd dictionary back to another bytearray 
    cfgBytes1 = RegisterPageConverter.readDictToPage( cfgDict1, Tmf8829ConfigRegs() )      

    # now do compare both dictionaries and both bytearrays
    compareDicts(cfgDict0, cfgDict1) 
    comparePages(cfgBytes0,cfgBytes1)

    # finally print the dictionary
    print( cfgDict0 )

