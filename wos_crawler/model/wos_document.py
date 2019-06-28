from sqlalchemy import Column, String, Integer, Text, ForeignKey, Table
from sqlalchemy.orm import relationship
from . import Base
import hashlib

inner_ref = Table('wos_inner_reference', Base.metadata,
                        Column('citing_paper_id', String(20), ForeignKey('wos_document.unique_id'), primary_key=True),
                        Column('cited_paper_id', String(20), ForeignKey('wos_document.unique_id'), primary_key=True))


class WosDocument(Base):
    __tablename__ = 'wos_document'

    # document_id = Column(Integer, primary_key=True)
    unique_id = Column(String(20), primary_key=True)
    title = Column(String(500))
    abs = Column(Text)
    journal = Column(String(255), index=True)
    journal_iso = Column(String(100))
    journal_29 = Column(String(50), index=True)
    publisher = Column(String(255))
    volume = Column(String(50)) # 有可能有AB卷
    issue = Column(String(10)) # 因为可能有SI：Special Issue，所以是String
    start_page = Column(String(10)) # 因为有可能是电子出版，页码包含E
    end_page = Column(String(10))
    pub_year = Column(Integer, index=True)
    pub_month_day = Column(String(10))
    document_type = Column(String(50))
    doi = Column(String(255), index=True)
    cited_times = Column(Integer)
    reference_num = Column(Integer)
    usage_180 = Column(Integer)
    usage_since_2013 = Column(Integer)
    # funding = Column(Text)
    funding_text = Column(Text)
    language = Column(String(20))
    author_email = Column(String(255))
    first_author = Column(String(255))
    document_md5 = Column(String(32), index=True)

    authors = relationship('WosAuthor', back_populates='document')
    categories = relationship('WosCategory', back_populates='document')
    research_areas = relationship('WosResearchArea', back_populates='document')
    keywords = relationship('WosKeyword', back_populates='document')
    keyword_plus = relationship('WosKeywordPlus', back_populates='document')
    references = relationship('WosReference', back_populates='document')
    fundings = relationship('WosFunding', back_populates='document')
    inner_references = relationship('WosDocument', secondary=inner_ref, backref='inner_citations',
                                    primaryjoin=unique_id == inner_ref.c.citing_paper_id,
                                    secondaryjoin=unique_id == inner_ref.c.cited_paper_id)

    def __init__(self, unique_id=None, title=None, abs=None, journal=None, journal_iso=None, journal_29=None,publisher=None,
                 volume=None, issue=None, start_page=None,end_page=None,pub_year=None, pub_month_day=None, document_type=None,
                 doi=None, cited_times=None, reference_num=None, usage_180=None, usage_since_2013=None,
                 funding_text=None, language=None, author_email=None, first_author=None):
        self.unique_id = unique_id
        self.title = title
        self.abs = abs
        self.journal = journal
        self.journal_iso = journal_iso
        self.journal_29 = journal_29
        self.publisher = publisher
        self.volume = volume
        self.issue = issue
        self.start_page = start_page
        self.end_page = end_page
        self.pub_year = pub_year
        self.pub_month_day = pub_month_day
        self.document_type = document_type
        self.doi = doi
        self.cited_times = cited_times
        self.reference_num = reference_num
        self.usage_180 = usage_180
        self.usage_since_2013 = usage_since_2013
        # self.funding = funding
        self.funding_text = funding_text
        self.language = language
        self.author_email = author_email
        self.first_author = first_author

    def __repr__(self):
        return '文章唯一ID：{}，标题：{}'.format(self.unique_id, self.title)


class WosAuthor(Base):
    __tablename__ = 'wos_author'

    author_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='authors')

    last_name = Column(String(255))
    first_name = Column(String(255))
    abbr_name = Column(String(255))
    author_order = Column(Integer)
    is_reprint_author = Column(Integer)
    affiliations = relationship('WosAffiliation', back_populates='author')

    def __init__(self, first_name, last_name, abbr_name,author_order, is_reprint_author):
        self.first_name = first_name
        self.last_name = last_name
        self.abbr_name = abbr_name
        self.author_order = author_order
        self.is_reprint_author = is_reprint_author

    def __repr__(self):
        return '文章{}的作者：{}, {}'.format(self.document_unique_id, self.last_name, self.first_name)


class WosCategory(Base):
    __tablename__ = 'wos_category'

    category_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='categories')

    category = Column(String(255), index=True)

    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return '文章{}的类别：{}'.format(self.document_unique_id, self.category)

class WosResearchArea(Base):
    __tablename__ = 'wos_research_area'

    area_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='research_areas')

    area = Column(String(255), index=True)

    def __init__(self, area):
        self.area = area

    def __repr__(self):
        return '文章{}的研究领域：{}'.format(self.document_unique_id, self.area)


class WosKeyword(Base):
    __tablename__ = 'wos_keyword'

    keyword_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='keywords')

    keyword = Column(String(255), index=True)

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return '文章{}的作者关键词：{}'.format(self.document_unique_id, self.keyword)


class WosKeywordPlus(Base):
    __tablename__ = 'wos_keyword_plus'

    keyword_plus_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='keyword_plus')

    keyword_plus = Column(String(255))

    def __init__(self, keyword_plus):
        self.keyword_plus = keyword_plus

    def __repr__(self):
        return '文章{}的Keyword Plus关键词：{}'.format(self.document_unique_id, self.keyword_plus)


class WosReference(Base):
    __tablename__ = 'wos_reference'

    reference_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='references')

    first_author = Column(String(255))
    pub_year = Column(Integer, index=True)
    journal = Column(String(255), index=True)
    volume = Column(String(50)) # 有可能有AB卷
    start_page = Column(String(100)) #因为有电子出版的可能，所以有可能是E开头
    doi = Column(String(255), index=True)
    document_md5 = Column(String(32), index=True)


    def __init__(self, first_author, pub_year, journal, volume, start_page, doi):
        self.first_author = first_author
        self.pub_year = pub_year
        self.journal = journal
        self.volume = volume
        self.start_page = start_page
        self.doi = doi
        if not first_author:
            first_author = ''
        if not journal:
            journal = ''
        if not volume:
            volume = ''
        if not start_page:
            start_page = ''
        if not pub_year:
            pub_year = ''
        if not doi:
            doi = ''
        self.document_md5 = hashlib.md5((','.join([first_author, journal, volume, start_page, pub_year, doi])).encode('utf-8')).hexdigest()

    def __repr__(self):
        return '文章{}的参考文献：{}, {}, {}, {}, {}, {}' \
            .format(self.document_unique_id, self.first_author, self.pub_year, self.journal, self.volume,
                    self.start_page, self.doi)


class WosAffiliation(Base):
    __tablename__ = 'wos_affiliation'

    affiliation_id = Column(Integer, primary_key=True, autoincrement=True)

    author_id = Column(Integer, ForeignKey('wos_author.author_id', ondelete='cascade', onupdate='cascade'))
    author = relationship('WosAuthor', back_populates='affiliations')

    address = Column(String(500))

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return '作者{}的机构：{}'.format(self.author_id, self.address)


class WosFunding(Base):
    __tablename__ = 'wos_funding'

    funding_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String(20), ForeignKey('wos_document.unique_id', ondelete='cascade', onupdate='cascade'))
    document = relationship('WosDocument', back_populates='fundings')

    agent = Column(String(500))
    funding_number = Column(String(255))

    def __init__(self, agent, funding_number):
        self.agent = agent
        self.funding_number = funding_number

    def __repr__(self):
        return '文章{}的基金：{}'.format(self.document_unique_id, self.agent + ': ' + self.funding_number if self.funding_number is not None else 'None')
