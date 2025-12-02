#!/usr/bin/env python3
# test_parsing.py - Test the HTML parsing functionality

import json
from app.support.parser.utils.html_parser import parse_html_to_dict

# Example HTML from the user's request
sample_html = """<div id="cont_txt">
<h1>водка Экстра классика</h1><h2>Федеральный реестр алкогольной продукции</h2><p style="background-color: #ffff99; font-size: 13px; padding: 0px;">Федеральная государственная информационная система «Федеральный реестр алкогольной продукции» (далее – ФРАП), выведена из эксплуатации приказом Росалкогольрегулирования от 29.10.2021 № 383.</p>
<div style="width: 300px; padding-bottom: 30px; padding-top: 20px;"><form action="/federalnyi-reestr-alkogolnoi-produktcii/search.html" class="search" method="post"><input class="input" name="str" placeholder="Поиск в реестре" type="text"/><input class="submit" name="" type="submit" value=""/></form></div>
<h4>Сведения из реестра:</h4>
<p></p>
<div style="padding: 10px; font-size: 13px;"><em>
<div class="two_sixth first">Регистрационный номер (номер реестровой записи уведомления о начале оборота на территории Российской Федерации алкогольной продукции в системе)</div>
<div class="three_fifth">02-00011120</div> <div class="two_sixth first">Уведомление (номер уведомления о начале оборота на территории Российской Федерации алкогольной продукции организации)</div>
<div class="three_fifth">№ 131 от 07.10.2013</div> <div class="two_sixth first">Уведомитель (полное и сокращенное наименование организации представившей уведомление о начале оборота на территории Российской Федерации алкогольной продукции)</div>
<div class="three_fifth">ОАО "БАШСПИРТ"</div> <div class="two_sixth first">Производители (полное и сокращенное наименование производтеля алкогольной продукции)</div>
<div class="three_fifth">РОССИЯ 0276100884/025745001 Бирский филиал АО "Башспирт"</div> <div class="two_sixth first">Наименование продукции (присвоенное производителем и предназначенное для обозначения алкогольной продукции слово или группа слов, под которыми она выпускается в оборот)</div>
<div class="three_fifth">водка "Экстра классика"</div> <div class="two_sixth first">Наименование на языке производителя</div>
<div class="three_fifth">водка "EXTRA CLASSICA"</div> <div class="two_sixth first">Крепость от (минимальное содержание этилового спирта (процентов) в алкогольной продукции )</div>
<div class="three_fifth">40</div> <div class="two_sixth first">Крепость до (максимальное содержание этилового спирта (процентов) в алкогольной продукции )</div>
<div class="three_fifth">40</div> <div class="two_sixth first">Емкости (объем и наименование емкости в которую разлита алкогольная продкуция)</div>
<div class="three_fifth">0.5000, стеклянная бутылка</div> <div class="two_sixth first">Состав (перечень компонетов алкогольной продукции (для винных напитков, пива и пивных напитков - доли (проценты) используемых компонентов на момент производства алкогольной продукции))</div>
<div class="three_fifth">вода питьевая исправленная : 60 процентов спирт этиловый ректификованный из пищевого сырья \"Люкс\": 40 процентов сахарный сироп:  лактоза:  кислота лимонная: </div> <div class="two_sixth first">Срок годности (установленный производителем алкогольной продукции срок годности на данный вид алкогольной продукции)</div>
<div class="three_fifth">не ограничен</div> <div class="two_sixth first">Идентификационный  документ (наименование) (наименование документа, в соответствии с которым произведена алкогольная продукция, в том числе национальных или международных стандартов и иной технической документации)</div>
<div class="three_fifth">1.Производственный технологический регламент на производство водок и ликероводочных изделий 2. ГОСТ «Водки и водки особые. Технические условия» 3. РЦ по производству водки \"Экстра классика\"«EXTRA CLASSICA»,  ТИ по производству водки\"Экстра классика\" «EXTRA CLASSICA»</div> <div class="two_sixth first">Идентификационный документ (номер) (реквизиты документа, в соответствии с которым произведена алкогольная продукция)</div>
<div class="three_fifth">1.10-12292-99  2. 12713-2013 3.РЦ 2-01-097-10</div> <div class="two_sixth first">Температура от (минимальная температура хранения алкогольной продукции (градусов Цельсия))</div>
<div class="three_fifth">минус 15</div> <div class="two_sixth first">Температура до  (максимальная температура хранения алкогольной продукции (градусов Цельсия))</div>
<div class="three_fifth">плюс 30</div> <div class="two_sixth first">Влажность (относительная влажность (процентов) хранения алкогольной продукции)</div>
<div class="three_fifth">85 процентов</div> <div class="two_sixth first">Категория алкогольной продукции</div>
<div class="three_fifth">водка</div> <div class="two_sixth first">Код ОКП</div>
<div class="three_fifth">91 8117 9</div> <div class="two_sixth first">Код ТН ВЭД ТС</div>
<div class="three_fifth">2208 60 110 0</div> <div class="two_sixth first">Вид алкогольной продукции по 171 федеральному закону</div>
<div class="three_fifth">200</div> <div class="two_sixth first">Декларация</div>
<div class="three_fifth">Декларация о соответствии №РОСС RU.АЯ36.Д17197,сертификат соответствия  №РОСС RU.АЯ36.Н29757</div> <div class="two_sixth first">Дата первой поставки</div>
<div class="three_fifth">30.10.2013 00:00:00</div> <div class="two_sixth first">Сведения о товарном знаке</div>
<div class="three_fifth">Товарный знак \"Экстра\" №258293 от 12.02.2013г.,лицензионный договор №0539-БС 5-л/э от 15.05.2012г, правообладатель ФКП Союзплодоимпорт</div> <div class="two_sixth first">Условия перевозки алкогольной продукции </div>
<div class="three_fifth">транспортирование  водки \"Экстра классика\"«EXTRA CLASSICA» осуществляют в соответствии  с ГОСТ  32098-2013 «Водки  и водки особые. Изделия  ликероводочные. Упаковка, маркировка, транспортирование  и хранение».</div> <div class="two_sixth first">Условия реализации алкогольной продукции</div>
<div class="three_fifth">Реализация при соблюдении условий хранения и сроков годности, установленных изготовителем</div> <div class="two_sixth first">Условия утилизации алкогольной продукции</div>
<div class="three_fifth">Согласно статьи 25 Федерального закона от 2 января 2000 г. № 29-ФЗ «О качестве и безопасности пищевых продуктов», статьи 18 Технического регламента Таможенного Союза ТР ТС 021/2011 «О безопасности пищевой продукции», утвержденного комиссией Таможенного Союза от 9 декабря 2011 г. № 880, а также пункта 6 статьи 2 Федерального Закона от 10 января 2002 года  № 7-ФЗ «Об охране окружающей среды».</div> <div class="two_sixth first">Маркировка, фото, подробная информация</div>
<div class="three_fifth"><a href="/federalnyi-reestr-alkogolnoi-produktcii/download/06A30F1A-2042-4E49-8A7F-CB815F846F71" title="Скачать файл маркировки алкогольной продукции">Скачать</a> </div></em></div>
<div class="full_width clear"></div>
<p> </p>
<p></p>
<div class="adfinity_block_9680"></div> </div>"""

if __name__ == "__main__":
    print("Testing HTML parsing function...")
    
    parsed_dict, field_mapping = parse_html_to_dict(sample_html)
    
    print("\nParsed dictionary:")
    print(json.dumps(parsed_dict, ensure_ascii=False, indent=2))
    
    print("\nField mapping:")
    print(json.dumps(field_mapping, ensure_ascii=False, indent=2))
    
    print(f"\nTotal keys found: {len(parsed_dict)}")
    print("Sample key-value pairs:")
    for key, value in list(parsed_dict.items())[:5]:  # Show first 5 pairs
        print(f"  '{key}': '{value}'")