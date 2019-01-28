from sqlalchemy import Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from . import Base


class WosDocument(Base):
    __tablename__ = 'wos_document'

    document_id = Column(Integer, primary_key=True)
    unique_id = Column(String)
    title = Column(String)
    abs = Column(Text)
    journal = Column(String)
    journal_iso = Column(String)
    publisher = Column(String)
    volume = Column(Integer)
    issue = Column(String) # 因为可能有SI：Special Issue，所以是String
    pub_year = Column(Integer)
    pub_month_day = Column(String)
    document_type = Column(String)
    doi = Column(String)
    cited_times = Column(Integer)
    reference_num = Column(Integer)
    usage_180 = Column(Integer)
    usage_since_2013 = Column(Integer)
    # funding = Column(Text)
    funding_text = Column(Text)
    language = Column(String)
    author_email = Column(String)

    authors = relationship('WosAuthor', back_populates='document')
    categories = relationship('WosCategory', back_populates='document')
    research_areas = relationship('WosResearchArea', back_populates='document')
    keywords = relationship('WosKeyword', back_populates='document')
    keyword_plus = relationship('WosKeywordPlus', back_populates='document')
    references = relationship('WosReference', back_populates='document')
    fundings = relationship('WosFunding', back_populates='document')

    def __init__(self, unique_id, title, abs, journal, journal_iso, publisher,
                 volume, issue, pub_year, pub_month_day, document_type,
                 doi, cited_times, reference_num, usage_180, usage_since_2013,
                 funding_text, language, author_email):
        self.unique_id = unique_id
        self.title = title
        self.abs = abs
        self.journal = journal
        self.journal_iso = journal_iso
        self.publisher = publisher
        self.volume = volume
        self.issue = issue
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

    def __repr__(self):
        return '文章编号：{}，唯一ID：{}，标题：{}'.format(self.document_id, self.unique_id, self.title)


class WosAuthor(Base):
    __tablename__ = 'wos_author'

    author_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='authors')

    last_name = Column(String)
    first_name = Column(String)
    author_order = Column(Integer)
    is_reprint_author = Column(Integer)
    affiliations = relationship('WosAffiliation', back_populates='author')

    def __init__(self, first_name, last_name, author_order, is_reprint_author):
        self.first_name = first_name
        self.last_name = last_name
        self.author_order = author_order
        self.is_reprint_author = is_reprint_author

    def __repr__(self):
        return '文章{}的作者：{}, {}'.format(self.document_unique_id, self.last_name, self.first_name)


class WosCategory(Base):
    __tablename__ = 'wos_category'

    category_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='categories')

    category = Column(String)

    def __init__(self, category):
        self.category = category

    def __repr__(self):
        return '文章{}的类别：{}'.format(self.document_unique_id, self.category)

class WosResearchArea(Base):
    __tablename__ = 'wos_research_area'

    category_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='research_areas')

    area = Column(String)

    def __init__(self, area):
        self.area = area

    def __repr__(self):
        return '文章{}的研究领域：{}'.format(self.document_unique_id, self.area)


class WosKeyword(Base):
    __tablename__ = 'wos_keyword'

    keyword_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='keywords')

    keyword = Column(String)

    def __init__(self, keyword):
        self.keyword = keyword

    def __repr__(self):
        return '文章{}的作者关键词：{}'.format(self.document_unique_id, self.keyword)


class WosKeywordPlus(Base):
    __tablename__ = 'wos_keyword_plus'

    keyword_plus_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='keyword_plus')

    keyword_plus = Column(String)

    def __init__(self, keyword_plus):
        self.keyword_plus = keyword_plus

    def __repr__(self):
        return '文章{}的Keyword Plus关键词：{}'.format(self.document_unique_id, self.keyword_plus)


class WosReference(Base):
    __tablename__ = 'wos_reference'

    reference_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='references')

    first_author = Column(String)
    pub_year = Column(Integer)
    journal = Column(String)
    volume = Column(Integer)
    start_page = Column(Integer)
    doi = Column(String)

    def __init__(self, first_author, pub_year, journal, volume, start_page, doi):
        self.first_author = first_author
        self.pub_year = pub_year
        self.journal = journal
        self.volume = volume
        self.start_page = start_page
        self.doi = doi

    def __repr__(self):
        return '文章{}的参考文献：{}, {}, {}, {}, {}, {}' \
            .format(self.document_unique_id, self.first_author, self.pub_year, self.journal, self.volume,
                    self.start_page, self.doi)


class WosAffiliation(Base):
    __tablename__ = 'wos_affiliation'

    affiliation_id = Column(Integer, primary_key=True, autoincrement=True)

    author_id = Column(Integer, ForeignKey('wos_author.author_id'))
    author = relationship('WosAuthor', back_populates='affiliations')

    address = Column(String)

    def __init__(self, address):
        self.address = address

    def __repr__(self):
        return '作者{}的机构：{}'.format(self.author_id, self.address)


class WosFunding(Base):
    __tablename__ = 'wos_funding'

    funding_id = Column(Integer, primary_key=True, autoincrement=True)

    document_unique_id = Column(String, ForeignKey('wos_document.unique_id'))
    document = relationship('WosDocument', back_populates='fundings')

    agent = Column(String)
    funding_number = Column(String)

    def __init__(self, agent, funding_number):
        self.agent = agent
        self.funding_number = funding_number

    def __repr__(self):
        return '文章{}的基金：{}'.format(self.document_unique_id, self.agent + ': ' + self.funding_number)
