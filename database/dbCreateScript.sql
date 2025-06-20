CREATE TABLE IF NOT EXISTS "Affiliation" (
	"ID"	INTEGER,
	"SourceID"	TEXT,
	"SourceURL"	TEXT,
	"Name"	TEXT NOT NULL,
	"Country"	TEXT,
	"City"	TEXT,
	"InsertID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Insert" FOREIGN KEY("InsertID") REFERENCES "InsertLog"("ID")
);
CREATE TABLE IF NOT EXISTS "Article" (
	"ID"	INTEGER,
	"SourceID"	TEXT,
	"SourceURL"	TEXT,
	"Name"	TEXT NOT NULL,
	"PublishDate"	TEXT,
	"ISSN"	INTEGER,
	"EISSN"	INTEGER,
	"DOI" TEXT,
	"Publisher" TEXT,
	"Volume"	INTEGER,
	"Description"	TEXT,
	"Type"	TEXT,
	"SubType"	TEXT,
	"CitedByCount"	INTEGER,
	"Sponsor"	TEXT,
	"InsertID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Insert" FOREIGN KEY("InsertID") REFERENCES "InsertLog"("ID")
);
CREATE TABLE IF NOT EXISTS "ArticlexAffiliation" (
	"ID"	INTEGER,
	"ArticleID"	INTEGER NOT NULL,
	"AffiliationID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Affiliation" FOREIGN KEY("AffiliationID") REFERENCES "Affiliation"("ID"),
	CONSTRAINT "FK_Article" FOREIGN KEY("ArticleID") REFERENCES "Article"("ID")
);
CREATE TABLE IF NOT EXISTS "ArticlexAuthor" (
	"ID"	INTEGER,
	"ArticleID"	INTEGER NOT NULL,
	"AuthorID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Article" FOREIGN KEY("ArticleID") REFERENCES "Article"("ID"),
	CONSTRAINT "FK_Author" FOREIGN KEY("AuthorID") REFERENCES "Author"("ID")
);
CREATE TABLE IF NOT EXISTS "ArticlexKeywords" (
	"ID"	INTEGER,
	"ArticleID"	INTEGER NOT NULL,
	"KeywordsID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Article" FOREIGN KEY("ArticleID") REFERENCES "Article"("ID"),
	CONSTRAINT "FK_Keywords" FOREIGN KEY("KeywordsID") REFERENCES "Keywords"("ID")
);
CREATE TABLE IF NOT EXISTS "Author" (
	"ID"	INTEGER,
	"SourceID"	TEXT,
	"SourceURL"	TEXT,
	"FullName"	TEXT NOT NULL,
	"FirstName"	TEXT,
	"SureName"	TEXT,
	"Initials"	TEXT,
	"InsertID"	INTEGER NOT NULL,
	PRIMARY KEY("ID" AUTOINCREMENT),
	CONSTRAINT "FK_Insert" FOREIGN KEY("InsertID") REFERENCES "InsertLog"("ID")
);
CREATE TABLE IF NOT EXISTS "InsertLog" (
	"ID"	INTEGER,
	"InsertTimestamp"	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
	"ArticleInsertCount"	INTEGER,
	"Source"	TEXT,
	PRIMARY KEY("ID" AUTOINCREMENT)
);
CREATE TABLE IF NOT EXISTS "Keywords" (
	"ID"	INTEGER NOT NULL,
	"Keyword"	TEXT,
	"InsertID"	INTEGER NOT NULL,
	PRIMARY KEY("ID"),
	CONSTRAINT "FK_Insert" FOREIGN KEY("InsertID") REFERENCES "InsertLog"("ID")
);
CREATE INDEX idx_author_sourceid ON Author(SourceID);
CREATE INDEX idx_affiliation_sourceid ON Affiliation(SourceID);
CREATE INDEX idx_keywords_keyword ON Keywords(Keyword);
