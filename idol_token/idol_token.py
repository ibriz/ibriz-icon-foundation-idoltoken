from iconservice import *

import abc

from iconservice import *
import uuid
import json

TAG = 'IdolToken'


class TokenStandard(abc.ABC):
    @abc.abstractmethod
    def name(self) -> str:
        pass

    @abc.abstractmethod
    def symbol(self) -> str:
        pass

    @abc.abstractmethod
    def balanceOf(self, _owner: Address) -> int:
        pass

    @abc.abstractmethod
    def totalSupply(self) -> int:
        pass

    @abc.abstractmethod
    def transfer(self, _to: Address, _tokenId: int):
        pass

    @abc.abstractmethod
    def ownerOf(self, _tokenId: int) -> Address:
        pass


class Idol(object):
    def __init__(self, _name, _age, _gender, _ipfs_handle):
        self.name = _name
        self.age = _age
        self.gender = _gender
        self.ipfs_handle = _ipfs_handle
        self.guuid = self.hash_idol()

    def hash_idol(self):
        return str(uuid.uuid1())


class IdolToken(IconScoreBase, TokenStandard):

    @eventlog(indexed=3)
    def Transfer(self, _from: Address, _to: Address, _tokenId: str):
        pass

    @eventlog(indexed=3)
    def Approval(self, _owner: Address, _approved: Address, _tokenId: str):
        pass

    def __init__(self, db: IconScoreDatabase) -> None:
        super().__init__(db)
        self._owner_address = VarDB("OWNER_ADDRESS", db, value_type=Address)
        self._token_approved = DictDB("TOKEN_APPROVED", db, value_type=Address)

        self._idolOwner = DictDB("IDOLOWNER", db, value_type=Address)
        self._ownerToIdolCount = DictDB("OWNERIDOLCOUNT", db, value_type=int)
        self._idolRegister = ArrayDB("IDOLLIST", db, value_type=str)
        self._idols = DictDB("IDOL", db, value_type=str, depth=2)

    def on_install(self, initialSupply: int, decimals: int) -> None:
        super().on_install()

    @external
    def create_idol(self, _name: str, _age: str, _gender: str, _ipfs_handle: str):
        idol = Idol(_name, _age, _gender, _ipfs_handle)
        # _tokenId = new_idol.hash_idol()
        # Use idol guuid to add attributes to DictDB
        # attribs = [a for a in dir(idol) if not a.startswith('__') and not callable(getattr(idol, a))]
        # attribs.remove('guuid')
        attribs = ["name", "age", "gender", "ipfs_handle", "guuid"]
        # _tokenId = len(self._idolRegister)
        _tokenId = idol.guuid
        self._idolRegister.put(idol.guuid)
        for attrib in attribs:
            self._idols[_tokenId][attrib] = getattr(idol, attrib)
        # _tokenId = str(self.totalSupply() + 1)
        self._idolOwner[_tokenId] = self.msg.sender
        self._ownerToIdolCount[self.msg.sender] += 1

    @external(readonly=True)
    def get_idol(self, _tokenId: str) -> str:
        # if _tokenId > len(self._idolRegister) or _tokenId < 0:
        #     return ""
        # return str(self._idols[_tokenId])
        attribs = ["owner", "name", "age", "gender", "ipfs_handle"]
        idol = {}
        for attrib in attribs:
            if attrib == "owner":
                idol[attrib] = str(self._idolOwner[_tokenId])
            else:
                idol[attrib] = self._idols[_tokenId][attrib]

        return json.dumps(idol)

    @external(readonly=True)
    def get_tokens_of_owner(self, _owner: Address) -> str:
        idol_token_list = []
        print('\nGetting tokens for owner: ' + str(_owner))
        print('Idols registered: '+str(len(self._idolRegister)))
        for _id in self._idolRegister:
            print('key|value : ' + str(_id)+':'+str(self._idolOwner[str(_id)]))
            if self._idolOwner[str(_id)] == _owner:
                idol_token_list.append(str(_id))

        return json.dumps({'idols': idol_token_list})

    def on_update(self) -> None:
        super().on_update()

    @external(readonly=True)
    def name(self) -> str:
        return "IdolToken"

    @external(readonly=True)
    def symbol(self) -> str:
        return "IDT"

    @external(readonly=True)
    def totalSupply(self) -> int:
        return len(self._idolRegister)

    @external(readonly=True)
    def balanceOf(self, _owner: Address) -> int:
        return self._ownerToIdolCount[_owner]

    @external(readonly=True)
    def ownerOf(self, _tokenId: int) -> Address:
        return self._idolOwner[_tokenId]

    @external(readonly=True)
    def getApproved(self, _tokenId: str) -> Address:
        return self._token_approved[_tokenId]

    @external
    def approve(self, _to: Address, _tokenId: str):
        tokenOwner = self._idolOwner[_tokenId]
        if tokenOwner != self.msg.sender:
            raise IconScoreException("approve : sender does not owns tokenId")

        self._token_approved[_tokenId] = _to
        self.Approval(self.msg.sender, _to, _tokenId)

    @external
    def transfer(self, _to: Address, _tokenId: str):
        idolOwner = self._idolOwner[_tokenId]
        if idolOwner != self.msg.sender:
            raise IconScoreException("transfer : sender does not owns tokenId")

        approved = self.getApproved(_tokenId)
        if approved != _to:
            raise IconScoreException("transfer : _to is not approved")

        self._idolOwner[_tokenId] = _to
        self._ownerToIdolCount[self.msg.sender] -= 1
        self._ownerToIdolCount[_to] += 1

        del self._token_approved[_tokenId]
        self.Transfer(self.msg.sender, _to, _tokenId)

    @external
    def transferFrom(self, _from: Address, _to: Address, _tokenId: str):
        idolOwner = self._idolOwner[_tokenId]
        if idolOwner != _from:
            raise IconScoreException("transfer : _from does not owns tokenId")

        approved = self.getApproved(_tokenId)
        if approved != _to:
            raise IconScoreException("transfer : _to is not approved")

        self._idolOwner[_tokenId] = _to
        self._ownerToIdolCount[_from] -= 1
        self._ownerToIdolCount[_to] += 1

        del self._token_approved[_tokenId]
        self.Transfer(_from, _to, _tokenId)
