from iconservice import *

TAG = 'IdolToken'


class TokenStandard(ABC):
    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def symbol(self) -> str:
        pass

    @abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    @abstractmethod
    def ownerOf(self, _tokenId: int) -> Address:
        pass

    @abstractmethod
    def getApproved(self, _tokenId: int) -> Address:
        pass

    @abstractmethod
    def approve(self, _to: Address, _tokenId: int):
        pass

    @abstractmethod
    def transfer(self, _to: Address, _tokenId: int):
        pass

    @abstractmethod
    def transferFrom(self, _from: Address, _to: Address, _tokenId: int):
        pass

class IdolToken(IconScoreBase, TokenStandard):

    _OWNER_ADDRESS="owner_address"
    _TOKEN_APPROVED="token_approved"
    _IDOL_OWNER="idol_owner"
    _OWNER_IDOL_COUNT="owner_idol_count"
    _IDOL_LIST="idol_list"
    _IDOL="idol"
    _ZERO_ADDRESS = Address.from_prefix_and_int(AddressPrefix.EOA, 0)

    

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._owner_address = VarDB(self._OWNER_ADDRESS, db, value_type=Address)
        self._token_approved = DictDB(self._TOKEN_APPROVED, db, value_type=Address)
        self._idolOwner = DictDB(self._IDOL_OWNER, db, value_type=Address)
        self._ownerToIdolCount = DictDB(self._OWNER_IDOL_COUNT, db, value_type=int)
        self._idolRegister = ArrayDB(self._IDOL_LIST, db, value_type=str)
        self._idols = DictDB(self._IDOL, db, value_type=str, depth=2)


    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _tokenId: int):
        pass

    @eventlog(indexed=3)
    def Approval(self, _owner: Address, _approved: Address, _tokenId: int):
        pass 
    
    def on_install(self, initialSupply: int, decimals: int) -> None:
        super().on_install()
    
    def on_update(self) -> None:
        super().on_update()


    @external
    def create_idol(self, _name: str, _age: str, _gender: str, _ipfs_handle: str):
        # Use token index as unique identifier to add attributes to DictDB
        attribs = {"name": _name, "age": _age, "gender": _gender, "ipfs_handle": _ipfs_handle}
        _tokenId = str(self.totalSupply() + 1)
        self._idolRegister.put(_tokenId)
        # for attrib in attribs:
        #     self._idols[_tokenId][attrib] = attribs[attrib]
        self._idolOwner[_tokenId] = self.msg.sender
        self._ownerToIdolCount[self.msg.sender] += 1
        self._idols[_tokenId]["attributes"]=json_dumps(attribs)


    @external(readonly=True)
    def get_idol(self, _tokenId: int) -> dict:
        if not self._id_validity(_tokenId):
            IconScoreException("idol details : invalid id")
        idol_attribs = {}
        idol_attribs=json_loads(self._idols[str(_tokenId)]["attributes"])
        idol_attribs["owner"]=self.ownerOf(_tokenId)
        return idol_attribs


    @external(readonly=True)
    def get_tokens_of_owner(self, _owner: Address) -> dict:
        idol_token_list = []
        for _id in self._idolRegister:
            if self._idolOwner[str(_id)] == _owner:
                idol_token_list.append(str(_id))

        return {'idols': idol_token_list}

    @external(readonly=True)
    def name(self) -> str:
        return "IdolToken"

    @external(readonly=True)
    def symbol(self) -> str:
        return "IDOL"

    @external(readonly=True)
    def totalSupply(self) -> int:
        return len(self._idolRegister)

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        if _owner is None or  self._is_zero_address(_owner):
            revert("Invalid owner address")
        return self._ownerToIdolCount[_owner]

    @external(readonly=True)
    def ownerOf(self, _tokenId: int) -> Address:
        if not  (self._id_validity(_tokenId)):
            revert("Invalid tokenId")
        return self._idolOwner[str(_tokenId)]

    @external(readonly=True)
    def getApproved(self, _tokenId: int) -> Address:
        if not (self._id_validity(_tokenId)):
            revert("Invalid tokenId")
        addr=self._token_approved[str(_tokenId)]
        if addr is None:
            return self._ZERO_ADDRESS
        return addr

    @external
    def approve(self, _to: Address, _tokenId: int):
        tokenOwner = self._idolOwner[str(_tokenId)]
        if tokenOwner != self.msg.sender:
            raise IconScoreException("approve : sender does not own the token")
        if _to==tokenOwner:
            raise IconScoreException("approve : cant approve to token owner")
        self._token_approved[str(_tokenId)] = _to
        self.Approval(self.msg.sender, _to, _tokenId)

    @external
    def transfer(self, _to: Address, _tokenId: int):
        idolOwner = self.ownerOf(_tokenId)
        if idolOwner != self.msg.sender:
            raise IconScoreException("transfer : sender does not own the token")
        if self._is_zero_address(_to):
            raise IconScoreException("transfer : receiver cant be a zero address")
        approved = self.getApproved(_tokenId)
        if approved != _to:
            raise IconScoreException("transfer : _to is not approved")
        self._transfer(self.msg.sender,_to,_tokenId)

    @external
    def transferFrom(self, _from: Address, _to: Address, _tokenId: str):
        idolOwner = self.ownerOf(_tokenId)
        if idolOwner != _from:
            raise IconScoreException("transfer : _from does not own the token")
        if idolOwner!=self.msg.sender and self._token_approved[str(_tokenId)]!=self.msg.sender:
            raise IconScoreException("transfer : unauthorised user for trasfer")
        approved = self.getApproved(_tokenId)
        if approved != _to:
            raise IconScoreException("transfer : _to is not approved")
        self._transfer(_from,_to,_tokenId)

    def _transfer(self,_from:Address,_to:Address,_tokenId:int):
        self._idolOwner[str(_tokenId)]=_to
        self._ownerToIdolCount[_to]+=1
        self._ownerToIdolCount[_from]-=1
        del self._token_approved[str(_tokenId)]
        self.Transfer(_from,_to,_tokenId)

    def _is_zero_address(self, _address: Address) -> bool:
    # Check if address is zero address
        if _address == self._ZERO_ADDRESS:
            return True
        return False

    def _id_validity(self,_tokenId)-> bool:
        if str(_tokenId) not in self._idolRegister:
            return False
        return True