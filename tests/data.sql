INSERT INTO user (mail, password, firstname, lastname)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'fname', 'lname'),
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', 'john', 'doe');

INSERT INTO bat (name, scientificname, user_id, description)
VALUES
    ('bat 1', 'name 1', 1, 'description 1'),
    ('bat 2', 'name 2', 1, 'description 2');

INSERT INTO terminal (name, location, user_id, information)
VALUES
    ('terminal 1', 'Louvain La Neuve FORET', 1, 'information 1'),
    ('terminal 2', 'Louvain La Neuve LAC', 1, 'information 2');

INSERT INTO detection(bat_id, terminal_id, information)
VALUES
    (1, 1, 'information LAC'),
    (2, 2, 'information FORET');