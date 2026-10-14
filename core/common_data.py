"""Të dhëna lokale për zbulimin e fjalëkalimeve të parashikueshme."""

COMMON_PASSWORDS = frozenset("""
123456 123456789 12345678 12345 1234567 1234567890 123123 111111 000000 654321
password password1 password123 passw0rd p@ssword qwerty qwerty123 qwertyuiop
admin admin123 administrator welcome welcome1 letmein monkey dragon master login
iloveyou sunshine princess football baseball abc123 1q2w3e4r 123qwe zaq12wsx
trustno1 shadow ashley michael jordan superman harley hunter charlie angel
whatever freedom mustang access flower hello hello123 secret guest root test
passw0rd password! password1234 qwerty1 qwerty12 qazwsx qazwsxedc asdfgh
asdfghjkl zxcvbnm 1qaz2wsx 1qazxsw2 qweasd qweasdzxc qazxsw 1q2w3e
987654321 987654 112233 121212 123321 123654 789456 159753 147258369
00000000 11111111 22222222 33333333 44444444 55555555 66666666 77777777
88888888 99999999 123123123 12345678910 123456789a 1password Password1
Password123 Password123! P@ssw0rd P@ssword1 P@ssword123 pass1234 pass123
changeme changeme1 default root123 toor secret123 user user123 guest123
computer internet service server database manager college university student
welcome123 access123 login123 loveyou iloveu iloveme jesus whatever1 nothing
starwars batman pokemon naruto soccer football1 baseball1 basketball1 tennis
summer summer2024 summer2025 winter spring autumn fall sunshine1 flower1
beautiful lovely love123 family friends whatever! qazwsx123 1qaz!QAZ qazwsx1
monkey1 monkey12 monkey123 dragon1 dragon12 dragon123 master1 master123
abc12345 abcdef abcdefg abcdefgh abcd1234 aaaaaa aaaaaaaa bbbbbbbb
1111 1234 12345 123456789012 0000 1212 7777 8888 9999 2580 0852 4321
shqiperia shqiperia1 shqiperia123 tirana tirana1 tirana123 kosova kosovo
albania albania123 shqiptar shqiptar1 durres vlora shkodra elbasani berat
prishtina prishtina123 shqiperi shqipe flamuri flamur123 shqiponja
emri mbiemri fjalekalim fjalkalim passwordi kompjuteri dashuri familja
123456a 123456b 123456c 654321a qwerty! qwerty@ qwerty12345 123qweasd
asdf1234 zxcv1234 zxcvbn 1q2w3e4r5t 1q2w3e4r5t6y 1qaz2wsx3edc
rootroot adminadmin admin1234 administrator1 welcome! welcome1234 letmein1
iloveyou1 princess1 michael1 shadow1 sunshine123 football123 baseball123
dragon2024 monkey2024 password2024 qwerty2024 admin2024 welcome2024
password2023 password2022 password2021 password2020 spring2024 summer2023
qwerty@123 pass@123456 P@ssw0rd123 qazwsx! asdfgh123 zxcvbn123
secret!123 login!123 user@1234 test1234 testtest test12345 hello!123
abcde12345 123abc 123abc456 123456abc 6543210 98765432 159357 753159
12131415 101010 010101 100000 200000 12344321 11223344 87654321
passwordpassword qwertyqwerty iloveyou123 iloveyou! mypassword mypassword1
yourname name123 surname123 birthday123 football2024 soccer2024 baseball2024
1q2w3e 1q2w3e4r5t 1qaz2wsx 1qaz!QAZ 1q2w3e4r! @#$%^&* qwe123!@#
police secret1 batman1 superman1 trustno1 abcdef123456 admin!@# root!123
married single welcomehome happy123 happybirthday birthday birthday1
pass123 password12 password22 password11 pass12345 passw0rd123 pass123456
123456789a 1234567890a 123456789! 12345678! 1234567! qwertyui 1q2w3e4r!
iloveyou! 123456789! admin@123 admin@1234 admin#123 admin123! guest guest1
qwerty123! P@ssword! p@ssw0rd! p@ssword123 welcome@123 roottoor abc@123
dragonball pokemon123 naruto123 hello world123 internet123 computer123
chocolate soccer1 football2 1234abcd 4321abcd 123456789q 987654321q
pass pass1234 pass12345 password!1 Password!1 Password123! qwerty!1
shqiperi123 tirana2024 tirana2025 albania2024 kosovo123 kosova123 besa123
testtest1 test123456 demo1234 sample1234 default1234 changeme123 letmein123
""".split())

KEYBOARD_SEQUENCES = (
    "qwerty", "asdf", "zxcv", "1qaz", "qazwsx", "qwertyuiop", "asdfghjkl",
    "zxcvbnm", "qweasdzxc", "1q2w3e", "1q2w3e4r", "1qaz2wsx",
)

DICTIONARY_WORDS = frozenset("""
password passw0rd admin welcome letmein monkey dragon master login shqiperia tirana
kosova kosovo albania shqiptar shqiperi shqipe dashuri family football baseball
sunshine princess shadow michael jordan superman hunter charlie hello secret
computer internet service server database manager college university student
summer winter spring autumn flower sunshine freedom whatever trustno access
beautiful lovely love family friends starwars batman pokemon naruto soccer
""".split())
