Bărbuceanu Constantin 332 CB
Tema1 ASC - Python Marketplace

============
# Organizare
============

Tema își propune implementarea unui marketplace care să funcționeze conform paradigmei Multi Producer Multi Consumer. Astfel, scheletul constă din 4 fișiere .py (marketplace.py, consumer.py, producer.py, product.py). Fisierul product.py conține definiția a 2 clase cu identificatorul dataclass, Coffee si Tea.

Implementarea temei folosește o abordare paralelă. Astfel, threadurile sunt de tip Producer si Consumer. Threadurile Producer rulează la infinit până când toate celelalte threaduri se termină. Acestea au rolul de a executa operația publish pe baza unor fișiere de input în care se specifică produsele care vor fi adăugate in marketplace. În același timp threadurile Consumer pot executa operațiile add_to_cart, remove_from_cart sau place_order conform specificațiilor din schelet.

Marketplace este clasa principală în care sunt implementate toate funcțiile de care se folosesc threadurile Consumer și Producer. La un moment de timp nu poate exista decât un singur marketplace.

Pe lângă valorile variabilelor primite din fișierele de input, clasa Marketplace mai conține următoarele date introduse de mine în rezolvare:

1. nr_products_dictionary : Un dicționar în care cheile sunt id-ul producătorului, iar valorile numărul de produse publicate de respectivul producător. Am folosit această variabilă pentru a ști când a fost atinsă limita de produse publicate impusă fiecărui producător.

2. carts_dictionary : Un dicționar în care cheile sunt id-uri de cart, iar valorile liste cu elemente de tip pereche (producer_id, product). Practic am folosit această structură pentru accesul rapid la orice cart existent.

3. list_of_products : O listă cu toate produsele existente în marketplace la un anumit moment.

4. cart_id_lock : Un mutex pe zona în care se creează un id de coș de cumpărături nou, prin incrementare.

        with self.cart_id_lock:
            self.cart_id = self.cart_id + 1
            self.carts_dictionary[self.cart_id] = []

        return self.cart_id

5. producer_id_lock : Un mutex pe zona în care se creeaza un id nou de producător, prin incrementare.
        
        with self.producer_id_lock:
            self.producer_id = self.producer_id + 1
            self.nr_products_dictionary[self.producer_id] = 0

        return self.producer_id

6. producer_id si cart_id : inițializate cu 0

7. remove_lock : Scopul acestui lock se adresează cazului în care mai mulți consumatori caută în același timp același produs, iar fără lock ar încerca să îl elimine simultan din lista globală de produse. Astfel, folosind lockul, doar unul va putea să facă asta, ceilalți fiind nevoiți să aștepte.

        for elem in self.list_of_products:
            #If it is there:
            if elem[1] == product:
                self.remove_lock.acquire()

                if self.list_of_products.count(elem) == 0:
                    self.remove_lock.release()
                    continue

                self.carts_dictionary[cart_id].append((elem[0], product))

                self.list_of_products.remove(elem)

                self.remove_lock.release()

                return True

        return False

Pe lângă acestea am mai folosit un lock si pe afișarea din Consumer a produselor cumpărate, deoarece print() nu este thread-safe conform informațiilor găsite pe Internet.

Consider că tema este una utilă pentru familiarizarea cu multithreading-ul în Python. De asemenea, subiectul temei este unul constructiv și de actualitate pentru ziua de azi.

Cred ca alegerea de a folosi dicționare acolo unde se poate aduce un boost de eficiență implementării, acestea fiind structuri de tip hashable. Dicționarele reprezintă practic cea mai rapida metodă din Python de a căuta în seturi de date mari cu multe entry-uri.

==============
# Implementare
==============

În rezolvarea temei am implementat întregul enunț. Mai exact am implementat toată partea de funcționalitate (80p), fapt vizibil prin trecerea tuturor testelor.

De asemenea, am creat și clasa de unitteste ASCMarketplace implementată în marketplace.py. Aceasta testează toate metodele clasei Marketplace, verificând rezultatul lor final pentru diverși parametri de intrare, precum și efectele lor laterale cum ar fi adăugarea/ștergerea din lista globală de produse sau golirea coșului de cumpărături, în place_order, echivalentă cu setarea listei de produse a coșului ca listă vidă. (10p)

De asemenea am implementat și funcționalitatea de logging. Am folosit RotatingFileHanler si conversia la gmtime. Am setat numărul maxim de copii istorice la 10 și dimensiunea maximă la 20 * 1024 bytes. De asemenea pentru afișare am folosit nivelul info.

Dificultăți întâmpinate:
========================

O dificultate întâmpinată a fost înțelegerea faptului ca Producerii au un regim de lucru continuu, execuția lor fiind oprită forțat la terminarea tuturor celorlalte threaduri ale programului. Mi-am dat seama de acest lucru când am observat în test.py că la creare au parametrul daemon = True.

O altă dificultate a constat în eliminarea erorii provocate în situația când mai mulți consumeri încercau să pună în cartul propriu același produs. Unul reușea în mod evident primul, iar ceilalți când încercau sa dea remove aceluiași produs din lista globala de produse a marketplace-ului generau o eroare deoarece încercau să facă remove unui produs care nu mai exista. Acest lucru a fost soluționat cu ajutorul unui lock.

O altă dificultate a fost sa reușesc sa pun clasa de unitteste ASCMarketplace în același fișier market.py alături de clasa Marketplace. Mai exact dificultatea a apărut la importul modulului product și ține de modul în care funcționează în Python ierarhia proiectelor. Importarea modulului product este necesară doar pentru rularea unittestelor, așa că am folosit următoarea soluție:
        try:
            #For unittests
            import product as p
        except ModuleNotFoundError:
            #For checker (functionality tests)
            pass

Singurele 3 warninguri de linting care pot să apară sunt:
    -consumer.py:45:8: R1702: Too many nested blocks (6/5) (too-many-nested-blocks)
    -marketplace.py:137:0: R0902: Too many instance attributes (9/7) (too-many-instance-attributes)
    -marketplace.py:239:16: R1732: Consider using 'with' for resource-allocating operations (consider-using-with)

În toate 3 cazurile nu am găsit o soluție care să nu afecteze funcționalitatea programului. Punctajul global dat de pylint rulat pe tot folderul este 9.96, iar în particular pe fiecare fișier: 9.88 (markeplace.py), 9.68 (consumer.py), 10, 10.

Lucruri interesante descoperite:
================================

Mi s-a părut interesant să implementez funcționalitățile de logging și de unittesting.

===================
# Resurse utilizate
===================
https://stackoverflow.com/questions/70556519/log-files-get-reset-on-the-restart-of-the-application-instead-of-appending-the-n
https://stackoverflow.com/questions/12139648/python-logging-specifying-converter-attribute-of-a-log-formatter-in-config-file
https://stackoverflow.com/questions/25897335/why-doesnt-print-output-show-up-immediately-in-the-terminal-when-there-is-no-ne
https://stackoverflow.com/questions/818828/is-it-possible-to-make-a-for-loop-without-an-iterator-variable-how-can-i-mak
https://stackoverflow.com/questions/70178229/how-to-format-a-log-record-inside-emit-function-instead-of-creating-a-form
https://stackoverflow.com/questions/67284107/python-attributeerror-super-object-has-no-attribute-testnet-however-the-at
https://stackoverflow.com/questions/64951836/python-logging-attributeerror-module-logging-has-no-attribute-handlers
https://stackoverflow.com/questions/36873096/run-pylint-for-all-python-files-in-a-directory-and-all-subdirectories
https://stackoverflow.com/questions/7445742/runtimeerror-thread-init-not-called-when-subclassing-threading-thread
https://stackoverflow.com/questions/4142151/how-to-import-the-class-within-the-same-directory-or-sub-directory
https://stackoverflow.com/questions/6854658/explain-the-setup-and-teardown-python-methods-used-in-test-cases
https://stackoverflow.com/questions/47596952/using-linter-from-wsl-ubuntu-for-windows-in-visual-studio-code
https://stackoverflow.com/questions/16863742/run-unittest-from-a-python-program-via-a-command-line-option
https://stackoverflow.com/questions/28478234/python-define-unit-test-classes-together-with-code
https://stackoverflow.com/questions/3220284/how-to-customize-the-time-format-for-python-logging
https://stackoverflow.com/questions/5191830/how-do-i-log-a-python-error-with-debug-information
https://stackoverflow.com/questions/6321160/how-to-set-timestamps-on-gmt-utc-on-python-logging
https://stackoverflow.com/questions/30669474/beyond-top-level-package-error-in-relative-import
https://stackoverflow.com/questions/35520160/python-logging-performance-comparison-and-options
https://stackoverflow.com/questions/6729268/log-messages-appearing-twice-with-python-logging
https://stackoverflow.com/questions/61806875/how-do-you-run-unit-tests-in-python-in-the-repl
https://stackoverflow.com/questions/43865291/import-function-from-a-file-in-the-same-folder
https://stackoverflow.com/questions/5280178/how-do-i-load-a-file-into-the-python-console
https://stackoverflow.com/questions/24722212/python-cant-find-module-in-the-same-folder
https://stackoverflow.com/questions/44725483/what-exactly-does-super-return-in-python-3
https://stackoverflow.com/questions/43730484/add-dictionaries-to-empty-list-dict-value
https://stackoverflow.com/questions/70076892/python-logging-not-outputting-date-time
https://stackoverflow.com/questions/40088496/how-to-use-pythons-rotatingfilehandler
https://stackoverflow.com/questions/28330317/print-timestamp-for-logging-in-python
https://stackoverflow.com/questions/4067786/checking-on-a-thread-remove-from-list
https://stackoverflow.com/questions/16633911/does-python-logging-flush-every-log
https://stackoverflow.com/questions/29147442/how-to-fix-pylint-logging-not-lazy
https://stackoverflow.com/questions/5574702/how-do-i-print-to-stderr-in-python
https://stackoverflow.com/questions/22448731/how-do-i-create-a-pylintrc-file
https://stackoverflow.com/questions/29082268/python-time-sleep-vs-event-wait
https://stackoverflow.com/questions/35391086/python-how-to-solve-keyerror-2
https://stackoverflow.com/questions/53513/how-do-i-check-if-a-list-is-empty
https://stackoverflow.com/questions/16981921/relative-imports-in-python-3

http://docs.python.org/library/unittest.html?highlight=unittest#module-unittest
https://docs.python.org/3/library/logging.handlers.html#module-logging.handlers
https://docs.python.org/3/library/unittest.html#organizing-test-code
https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
https://docs.python.org/3/library/unittest.html#module-unittest
https://docs.python.org/3/library/unittest.html#assert-methods
https://docs.python.org/3/tutorial/interpreter.html
https://docs.python.org/3/library/threading.html
https://docs.python.org/3/library/logging.html
https://docs.python.org/3/howto/logging.html

https://www.google.com/search?client=firefox-b-d&q=are+python+dictionaries+efficient
https://www.google.com/search?client=firefox-b-d&q=is+print+thread+safe+python

https://realpython.com/python-flush-print-output/
https://realpython.com/python-data-classes/
https://realpython.com/python-not-operator/
https://realpython.com/python-time-module/
https://realpython.com/python-sleep/

https://superfastpython.com/thread-safe-list/#Most_List_Operations_Are_Atomic
https://superfastpython.com/thread-safe-logging-in-python/
https://superfastpython.com/lock-a-function-in-python/

https://www.w3schools.com/python/ref_func_range.asp
https://www.w3schools.com/python/python_tuples.asp
https://www.w3schools.com/python/python_sets.asp

https://www.freecodecamp.org/news/python-list-remove-how-to-remove-an-item-from-a-list-in-python/
https://www.codecademy.com/forum_questions/5428448c631fe926790011b7
https://coralogix.com/blog/python-logging-best-practices-tips/
https://www.loggly.com/ultimate-guide/python-logging-basics/
https://flexiple.com/python/python-list-contains/#section5
https://www.geeksforgeeks.org/file-flush-method-in-python/
https://iq-inc.com/importerror-attempted-relative-import/
https://www.educative.io/answers/what-is-super-in-python
https://devguide.python.org/testing/run-write-tests/
https://www.programiz.com/python-programming/tuple
https://fortierq.github.io/python-import/
https://www.pylint.org/
