from sqlalchemy import Column, BigInteger, ForeignKey
from database.base import Base


class UserCertificate(Base):
    __tablename__ = "user_certificate"

    user_id = Column(BigInteger, ForeignKey("user.id"), primary_key=True, comment="사용자 고유 식별값")
    certificate_id = Column(BigInteger, ForeignKey("certificate.id"), primary_key=True, comment="자격증 고유 식별값")
