from sqlalchemy import Column, String, Boolean, Integer

from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email_id = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    git_accounts = relationship('GitAccount', back_populates='user')


class GitAccount(Base):
    __tablename__ = 'git_accounts'

    id = Column(Integer, primary_key=True)
    provider = Column(String, nullable=False)
    auth_token = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship('User', back_populates='git_accounts')
    repositories = relationship('GitRepository', back_populates='git_account')


class GitRepository(Base):
    __tablename__ = 'git_repositories'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    git_account_id = Column(Integer, ForeignKey('git_accounts.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    git_account = relationship('GitAccount', back_populates='repositories')
    commits = relationship('GitCommit', back_populates='repository')


class GitCommit(Base):
    __tablename__ = 'git_commits'

    id = Column(Integer, primary_key=True)
    branch_name = Column(String, nullable=False)
    repository_id = Column(Integer, ForeignKey('git_repositories.id'), nullable=False)
    metric_file_id = Column(Integer, ForeignKey('metric_files.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    repository = relationship('GitRepository', back_populates='commits')
    metric_file = relationship('MetricFile', uselist=False, back_populates='commit')


class MetricFile(Base):
    __tablename__ = 'metric_files'

    id = Column(Integer, primary_key=True)
    file_hash = Column(String, nullable=False)
    repository_id = Column(Integer, ForeignKey('git_repositories.id'), nullable=False)
    file_data = Column(Text, nullable=False)  # Assuming JSON data is stored as text
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    commit = relationship('GitCommit', back_populates='metric_file')