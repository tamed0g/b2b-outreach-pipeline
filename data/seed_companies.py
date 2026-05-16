"""
Сид-список российских B2B SaaS / IT-сервисов для бизнеса.
Источник: публичные каталоги (startpack.ru, soware.ru, рейтинги Tagline/Рейтинг Рунета),
дополнено известными игроками рынка.

Структура: (название, домен, краткая категория)
Категория нужна, чтобы потом проще было сегментировать и писать персонализацию.
"""

COMPANIES = [
    # CRM / Sales automation
    ("Bitrix24",        "https://www.bitrix24.ru/",       "CRM"),
    ("amoCRM",          "https://www.amocrm.ru/",         "CRM"),
    ("Мегаплан",        "https://megaplan.ru/",            "CRM"),
    ("RetailCRM",       "https://www.retailcrm.ru/",       "CRM"),
    ("Pyrus",           "https://pyrus.com/ru",            "Workflow"),
    ("Planfix",         "https://planfix.com/ru/",         "Project mgmt"),
    ("Kaiten",          "https://kaiten.ru/",              "Project mgmt"),
    ("Yougile",         "https://yougile.com/",            "Project mgmt"),
    ("Weeek",           "https://weeek.net/",              "Project mgmt"),
    ("Worksection",     "https://worksection.com/ru/",     "Project mgmt"),

    # Marketing / Email / Communications
    ("Unisender",       "https://www.unisender.com/ru/",   "Email marketing"),
    ("SendPulse",       "https://sendpulse.com/ru",        "Email marketing"),
    ("Sendsay",         "https://sendsay.ru/",             "Email marketing"),
    ("DashaMail",       "https://dashamail.ru/",           "Email marketing"),
    ("Mindbox",         "https://mindbox.ru/",             "CDP / marketing"),
    ("Carrot quest",    "https://www.carrotquest.io/",     "Chat / marketing"),
    ("Envybox",         "https://envybox.io/",             "Lead capture"),
    ("Postoplan",       "https://postoplan.app/",          "SMM automation"),
    ("Click.ru",        "https://click.ru/",               "Ads automation"),
    ("Aitarget",        "https://aitarget.com/",           "Ads automation"),

    # Analytics / call tracking
    ("Roistat",         "https://roistat.com/",            "Marketing analytics"),
    ("Calltouch",       "https://www.calltouch.ru/",       "Call tracking"),
    ("Comagic",         "https://www.comagic.ru/",         "Call tracking"),
    ("Mango Office",    "https://www.mango-office.ru/",    "Telephony / CC"),
    ("Topvisor",        "https://topvisor.com/ru/",        "SEO analytics"),
    ("Rookee",          "https://www.rookee.ru/",          "SEO platform"),
    ("Promopult",       "https://promopult.ru/",           "SEO/Ads platform"),
    ("OWOX BI",         "https://www.owox.com/ru/",        "BI / analytics"),

    # HR-tech
    ("Huntflow",        "https://huntflow.ru/",            "ATS / HR"),
    ("Potok",           "https://potok.io/",               "ATS / HR"),
    ("Skillaz",         "https://skillaz.ru/",             "Recruiting automation"),
    ("E-Staff",         "https://e-staff.ru/",             "ATS"),
    ("iSpring",         "https://www.ispring.ru/",         "LMS / corp learning"),
    ("Teachbase",       "https://teachbase.ru/",           "LMS"),
    ("Эквио",           "https://www.equio.ru/",           "Corp learning"),

    # Customer support / live chat
    ("Jivo",            "https://www.jivo.ru/",            "Live chat"),
    ("WebIM",           "https://webim.ru/",               "Omni chat"),
    ("Verbox",          "https://verbox.ru/",              "Live chat"),
    ("LiveTex",         "https://livetex.ru/",             "Live chat"),
    ("Talk-Me",         "https://talk-me.ru/",             "Live chat"),
    ("Cleversite",      "https://cleversite.ru/",          "Live chat"),

    # eCommerce / website builders
    ("InSales",         "https://www.insales.ru/",         "eCommerce platform"),
    ("AdvantShop",      "https://www.advantshop.net/",     "eCommerce platform"),
    ("Tilda",           "https://tilda.cc/ru/",            "Site builder"),
    ("Flexbe",          "https://flexbe.com/",             "Site builder"),
    ("LPgenerator",     "https://lpgenerator.ru/",         "Landing builder"),

    # Cloud / hosting / infra
    ("Selectel",        "https://selectel.ru/",            "Cloud / hosting"),
    ("Timeweb",         "https://timeweb.com/",            "Cloud / hosting"),
    ("Beget",           "https://beget.com/ru",            "Hosting"),
    ("Reg.ru",          "https://www.reg.ru/",             "Domains / hosting"),
    ("Servercore",      "https://servercore.com/ru/",      "Cloud infra"),

    # Cybersecurity
    ("BI.ZONE",         "https://bi.zone/",                "Cybersecurity"),
    ("Positive Technologies", "https://www.ptsecurity.com/ru-ru/", "Cybersecurity"),
    ("Solar",           "https://rt-solar.ru/",            "Cybersecurity"),

    # Accounting / EDM / document mgmt
    ("МойСклад",        "https://www.moysklad.ru/",        "Inventory / ERP"),
    ("Контур",          "https://kontur.ru/",              "Accounting / EDM"),
    ("СБИС",            "https://sbis.ru/",                "EDM / accounting"),
    ("DocsVision",      "https://docsvision.com/",         "Document mgmt"),

    # Forms / feedback
    ("Anketolog",       "https://anketolog.ru/",           "Surveys"),
    ("Testograf",       "https://www.testograf.ru/",       "Surveys"),

    # Telephony / VoIP
    ("UIS",             "https://www.uiscom.ru/",          "Telephony / CC"),
    ("OnlinePBX",       "https://www.onlinepbx.ru/",       "Cloud PBX"),
    ("Zadarma",         "https://zadarma.com/ru/",         "Cloud PBX"),

    # Misc B2B SaaS
    ("Wrike",           "https://www.wrike.com/ru/",       "Project mgmt"),
    ("DocsInBox",       "https://docsinbox.ru/",           "EDM HoReCa"),
    ("Aspro",           "https://aspro.ru/",               "Business platform"),
]

if __name__ == "__main__":
    print(f"Всего компаний в сид-списке: {len(COMPANIES)}")
    from collections import Counter
    cats = Counter(c[2] for c in COMPANIES)
    for cat, n in cats.most_common():
        print(f"  {cat}: {n}")
