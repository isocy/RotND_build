from abc import ABC


class IKeyEvaluator(ABC):
    def RuntimeKeyIsValid(self):
        pass


class AssetReference(IKeyEvaluator):
    def __init__(self, m_SubObjectName, m_SubObjectType, m_AssetGUID=""):
        self.m_AssetGUID = m_AssetGUID
        self.m_SubObjectName = m_SubObjectName
        self.m_SubObjectType = m_SubObjectType
