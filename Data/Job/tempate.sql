--
-- File generated with SQLiteStudio v3.4.17 on CN Thg5 18 07:43:19 2025
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: company
CREATE TABLE IF NOT EXISTS company (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    Logo               TEXT,
    name               TEXT    NOT NULL,
    shortdescription   TEXT,
    curent_job_opening INTEGER,
    industry           TEXT,
    size               TEXT,
    nationality        TEXT,
    tech_stack         TEXT,
    website            TEXT,
    Social_media       TEXT,
    address            TEXT,
    description        TEXT,
    banner             TEXT,
    short_address      TEXT,
    followers          INTEGER,
    about_images       TEXT
);


-- Table: company_skills
CREATE TABLE IF NOT EXISTS company_skills (
    company_id INT,
    skill_id   INT,
    PRIMARY KEY (
        company_id,
        skill_id
    ),
    FOREIGN KEY (
        company_id
    )
    REFERENCES company (id),
    FOREIGN KEY (
        skill_id
    )
    REFERENCES skill (id) 
);


-- Table: contractType
CREATE TABLE IF NOT EXISTS contractType (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

INSERT INTO contractType (
                             id,
                             name
                         )
                         VALUES (
                             1,
                             'part time'
                         );

INSERT INTO contractType (
                             id,
                             name
                         )
                         VALUES (
                             2,
                             'freelance'
                         );

INSERT INTO contractType (
                             id,
                             name
                         )
                         VALUES (
                             3,
                             'fulltime'
                         );


-- Table: job
CREATE TABLE IF NOT EXISTS job (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL,
    name_company  TEXT    NOT NULL,
    id_company    INTEGER,
    address       TEXT,
    salary        TEXT,
    date_expire   TEXT,
    experience    TEXT,
    skill_id      INTEGER,
    job_type_id   INTEGER,
    level_id      INTEGER,
    contract_type INTEGER REFERENCES contractType (id),
    description   TEXT,
    logo          TEXT,
    FOREIGN KEY (
        skill_id
    )
    REFERENCES skill (id),
    FOREIGN KEY (
        job_type_id
    )
    REFERENCES jobType (id),
    FOREIGN KEY (
        level_id
    )
    REFERENCES level (id) 
);


-- Table: job_company
CREATE TABLE IF NOT EXISTS job_company (
    id_job             REFERENCES job (id),
    id_company INTEGER REFERENCES company (id) 
);


-- Table: job_jobtypes
CREATE TABLE IF NOT EXISTS job_jobtypes (
    job_id      INTEGER REFERENCES job (id),
    job_type_id INTEGER REFERENCES jobType (id) 
);


-- Table: job_levels
CREATE TABLE IF NOT EXISTS job_levels (
    job_id   INTEGER REFERENCES job (id),
    level_id         REFERENCES level (id) 
);


-- Table: job_skills
CREATE TABLE IF NOT EXISTS job_skills (
    job_id   INTEGER REFERENCES job (id),
    skill_id INTEGER REFERENCES skill (id) 
);


-- Table: jobType
CREATE TABLE IF NOT EXISTS jobType (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

INSERT INTO jobType (
                        id,
                        name
                    )
                    VALUES (
                        1,
                        'In Office'
                    );

INSERT INTO jobType (
                        id,
                        name
                    )
                    VALUES (
                        2,
                        'Hybrid'
                    );

INSERT INTO jobType (
                        id,
                        name
                    )
                    VALUES (
                        3,
                        'Remote'
                    );

INSERT INTO jobType (
                        id,
                        name
                    )
                    VALUES (
                        4,
                        'Oversea'
                    );


-- Table: level
CREATE TABLE IF NOT EXISTS level (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      1,
                      'Intern'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      2,
                      'Fresher'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      3,
                      'Junior'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      4,
                      'Middle'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      5,
                      'Senior'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      6,
                      'Tru?ng Nhóm'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      7,
                      'Tru?ng phòng'
                  );

INSERT INTO level (
                      id,
                      name
                  )
                  VALUES (
                      8,
                      'All Levels'
                  );


-- Table: location
CREATE TABLE IF NOT EXISTS location (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

INSERT INTO location (
                         id,
                         name
                     )
                     VALUES (
                         1,
                         'H? Chí Minh'
                     );

INSERT INTO location (
                         id,
                         name
                     )
                     VALUES (
                         2,
                         'Hà N?i'
                     );

INSERT INTO location (
                         id,
                         name
                     )
                     VALUES (
                         3,
                         'Ðà N?ng'
                     );

INSERT INTO location (
                         id,
                         name
                     )
                     VALUES (
                         4,
                         'C?n Tho'
                     );

INSERT INTO location (
                         id,
                         name
                     )
                     VALUES (
                         5,
                         'Khác'
                     );


-- Table: skill
CREATE TABLE IF NOT EXISTS skill (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT
);

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      1,
                      'JavaScript'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      2,
                      'Java'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      3,
                      '.NET'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      4,
                      'C#'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      5,
                      'PHP'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      6,
                      'Python'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      7,
                      'C++'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      8,
                      'iOS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      9,
                      'Android'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      10,
                      'Mobile'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      11,
                      'Flutter'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      12,
                      'React Native'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      13,
                      'Tester'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      14,
                      'Product Manager'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      15,
                      'Business Analyst'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      16,
                      'Project Manager'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      17,
                      'System Admin'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      18,
                      'DevOps'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      19,
                      'System Engineer'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      20,
                      'Data Analyst'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      21,
                      'Game'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      22,
                      'Designer'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      23,
                      'Golang'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      24,
                      'AWS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      25,
                      'Azure'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      26,
                      'Cloud'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      27,
                      'UI/UX'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      28,
                      'HTML'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      29,
                      'Unity'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      30,
                      'Kotlin'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      31,
                      'IT Security'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      32,
                      'IT Support'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      33,
                      'IT helpdesk'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      34,
                      'ERP'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      35,
                      'Solution Architect'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      36,
                      'Database'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      37,
                      'Xamarin'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      38,
                      'Front-End'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      39,
                      'Back-End'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      40,
                      'QA QC'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      41,
                      'NodeJS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      42,
                      'ReactJS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      43,
                      'VueJS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      44,
                      'SQL'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      45,
                      'Laravel'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      46,
                      'ASP.NET'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      47,
                      'Angular'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      48,
                      'AngularJS'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      49,
                      'SAP'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      50,
                      'Magento'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      51,
                      'WordPress'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      52,
                      'Network'
                  );

INSERT INTO skill (
                      id,
                      name
                  )
                  VALUES (
                      53,
                      'Embedded'
                  );


COMMIT TRANSACTION;
PRAGMA foreign_keys = on;
