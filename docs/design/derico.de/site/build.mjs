import { mkdir, writeFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));

const slugs = {
  de: {
    home: "index.html",
    services: "leistungen.html",
    odoo: "odoo.html",
    odooDevelopment: "odoo-entwicklung.html",
    odooConsulting: "odoo-beratung.html",
    odooOperations: "odoo-betrieb.html",
    plone: "plone.html",
    ploneDevelopment: "plone-entwicklung.html",
    ploneConsulting: "plone-beratung.html",
    ploneOperations: "plone-betrieb.html",
    python: "python.html",
    sustainability: "nachhaltigkeit.html",
    care: "support-wartung.html",
    support: "support.html",
    maintenance: "wartung.html",
    knowledge: "schulungen-vortraege.html",
    training: "schulungen.html",
    talks: "vortraege.html",
    contact: "kontakt.html",
    imprint: "impressum.html",
    styleguide: "styleguide.html",
  },
  en: {
    home: "index.html",
    services: "services.html",
    odoo: "odoo.html",
    odooDevelopment: "odoo-development.html",
    odooConsulting: "odoo-consulting.html",
    odooOperations: "odoo-operations.html",
    plone: "plone.html",
    ploneDevelopment: "plone-development.html",
    ploneConsulting: "plone-consulting.html",
    ploneOperations: "plone-operations.html",
    python: "python.html",
    sustainability: "sustainability.html",
    care: "support-maintenance.html",
    support: "support.html",
    maintenance: "maintenance.html",
    knowledge: "training-talks.html",
    training: "training.html",
    talks: "talks.html",
    contact: "contact.html",
    imprint: "legal-notice.html",
    styleguide: "styleguide.html",
  },
};

const navigation = {
  de: {
    skip: "Zum Inhalt springen",
    menu: "Menü",
    homeLabel: "derico.de Startseite",
    services: {
      label: "Leistungen",
      intro: "Anwendungsentwicklung mit offenem Fundament und einem klaren Plan für die Jahre nach dem Start.",
      overview: "Alle Leistungen",
      proof: "Zwanzig Jahre Python-Erfahrung fließen in Architektur, Betrieb und Weiterentwicklung ein.",
      links: [
        ["odoo", "Odoo", "Geschäftsprozesse verbinden und dauerhaft weiterentwickeln", [["odooDevelopment", "Entwicklung"], ["odooConsulting", "Beratung"], ["odooOperations", "Betrieb"]]],
        ["plone", "Plone", "Inhalte, Workflows und Berechtigungen verlässlich organisieren", [["ploneDevelopment", "Entwicklung"], ["ploneConsulting", "Beratung"], ["ploneOperations", "Betrieb"]]],
        ["python", "Django, Pyramid & FastAPI", "Passende Python-Architekturen für individuelle Anwendungen"],
      ],
    },
    sustainability: "Nachhaltigkeit",
    care: {
      label: "Support & Wartung",
      intro: "Verlässliche Betreuung für Anwendungen, die täglich gebraucht werden und mit ihrer Aufgabe wachsen.",
      overview: "Support & Wartung im Überblick",
      proof: "Pflege bleibt planbar: Zuständigkeiten, Reaktionswege und Upgrade-Zyklen werden gemeinsam festgelegt.",
      links: [
        ["support", "Support", "Direkte Hilfe durch Menschen, die Anwendung und Betrieb verstehen"],
        ["maintenance", "Wartung", "Updates, Sicherheit und technische Erneuerung mit langfristigem Horizont"],
      ],
    },
    knowledge: {
      label: "Schulungen & Vorträge",
      intro: "Erfahrung wird nutzbar, wenn Teams Zusammenhänge verstehen und Entscheidungen selbst tragen können.",
      overview: "Wissen weitergeben",
      proof: "Schulungen entstehen aus realen Projekten und Beiträgen zur Open-Source-Community.",
      links: [
        ["training", "Schulungen", "Formate für Teams, Administrator:innen und Entwickler:innen"],
        ["talks", "Vorträge", "Konferenzbeiträge, Themen und buchbare Sessions"],
      ],
    },
    contact: "Kontakt",
    searchOpen: "Suche öffnen",
    searchClose: "Suche schließen",
    searchField: "Suchbegriff",
    searchSubmit: "Suchen",
    firstTalk: "Erstgespräch vereinbaren",
    contactLead: "Sie schildern die Aufgabe. Wir klären gemeinsam, welcher nächste Schritt sinnvoll ist.",
    email: "E-Mail schreiben",
    location: "Neuhaus/Elbe · Deutschland",
    subnavTitle: "Mehr zum Thema:",
    footerLine: "Nachhaltige Lösungen für Anwendungen, die bleiben.",
    imprint: "Impressum",
  },
  en: {
    skip: "Skip to content",
    menu: "Menu",
    homeLabel: "derico.de home",
    services: {
      label: "Services",
      intro: "Application development with an open foundation and a clear plan for the years after launch.",
      overview: "All services",
      proof: "Twenty years of Python experience inform architecture, operations and continued development.",
      links: [
        ["odoo", "Odoo", "Connect business processes and develop them sustainably", [["odooDevelopment", "Development"], ["odooConsulting", "Consulting"], ["odooOperations", "Operations"]]],
        ["plone", "Plone", "Organise content, workflows and permissions reliably", [["ploneDevelopment", "Development"], ["ploneConsulting", "Consulting"], ["ploneOperations", "Operations"]]],
        ["python", "Django, Pyramid & FastAPI", "Purpose-fit Python architectures for individual applications"],
      ],
    },
    sustainability: "Sustainability",
    care: {
      label: "Support & maintenance",
      intro: "Dependable care for applications that matter every day and continue to grow with their task.",
      overview: "Support & maintenance overview",
      proof: "Care stays predictable: responsibilities, response paths and upgrade cycles are agreed together.",
      links: [
        ["support", "Support", "Direct help from people who understand the application and its operations"],
        ["maintenance", "Maintenance", "Updates, security and technical renewal with a long horizon"],
      ],
    },
    knowledge: {
      label: "Training & talks",
      intro: "Experience becomes useful when teams understand the connections and can carry decisions themselves.",
      overview: "Sharing knowledge",
      proof: "Training grows from real projects and contributions to open-source communities.",
      links: [
        ["training", "Training", "Formats for teams, administrators and developers"],
        ["talks", "Talks", "Conference sessions, topics and bookable presentations"],
      ],
    },
    contact: "Contact",
    searchOpen: "Open search",
    searchClose: "Close search",
    searchField: "Search term",
    searchSubmit: "Search",
    firstTalk: "Arrange an initial conversation",
    contactLead: "Tell us about the task. Together, we identify a useful next step.",
    email: "Write an email",
    location: "Neuhaus/Elbe · Germany",
    subnavTitle: "More on this topic:",
    footerLine: "Sustainable solutions for applications, grown to last.",
    imprint: "Legal notice",
  },
};

const pages = {
  de: {
    home: {
      type: "home",
      title: "Anwendungen, die bleiben.",
      context: "Nachhaltige Lösungen, seit über 20 Jahren",
      lede: "Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem JavaScript und Open Source. Wartbarkeit, offene Standards und klare Entscheidungen sichern ihren Wert über viele Jahre.",
    },
    services: {
      type: "overview",
      title: "Anwendungsentwicklung mit langem Horizont.",
      context: "Leistungen",
      lede: "Technologie ist tragfähig, wenn sie zur Aufgabe passt, verständlich bleibt und zuverlässig weiterentwickelt werden kann.",
      introTitle: "Drei erprobte Grundlagen",
      intro: "Wir wählen Frameworks nach Prozess, Organisation und Lebensdauer der Anwendung. Architektur, Benutzeroberfläche und Betrieb werden dabei als zusammenhängende Aufgabe geplant.",
      children: ["odoo", "plone", "python"],
    },
    odoo: {
      type: "detail",
      title: "Odoo verbindet Ihre Geschäftsprozesse.",
      context: "Leistungen · Odoo",
      lede: "Wir führen Odoo ein, entwickeln Module nach offenen OCA-Standards und halten das System über Versionswechsel hinweg anschlussfähig.",
      fit: "Vertrieb, Einkauf, Lager und Abrechnung",
      foundation: "Odoo · Python · OCA",
      horizon: "Einführung, Module und Upgrades",
      bodyTitle: "Ein System, das den tatsächlichen Ablauf trägt",
      body: [
        "Eine Odoo-Einführung beginnt mit den Arbeitsschritten, Zuständigkeiten und Daten, die Ihr Team täglich bewegt. Daraus entsteht eine klare Modulgrenze und eine Einführung in sinnvollen Etappen.",
        "Eigene Erweiterungen folgen den Konventionen der Odoo Community Association. Das erleichtert Tests, Reviews und spätere Versionswechsel. Dokumentierte Entscheidungen halten die Anwendung auch für neue Teammitglieder verständlich.",
      ],
      deliverables: ["Prozess- und Modulkonzept", "OCA-konforme Erweiterungen", "Datenmigration und Schnittstellen", "Einführung, Schulung und Upgrade-Plan"],
      childrenTitle: "Drei Einstiege, je nach Ausgangslage",
      children: ["odooDevelopment", "odooConsulting", "odooOperations"],
      quote: "Eine ERP-Einführung trägt, wenn Teams ihre tägliche Arbeit darin wiederfinden und jede Erweiterung einen nachvollziehbaren Platz hat.",
      proofLinks: [["https://odoo-community.org/", "Odoo Community Association"], ["knowledge", "Schulungen für Ihr Odoo-Team"]],
    },
    odooDevelopment: {
      type: "detail",
      title: "Odoo-Entwicklung für klare Prozesse.",
      context: "Leistungen · Odoo · Entwicklung",
      lede: "Wir entwickeln Odoo-Module und Schnittstellen, die fachliche Abläufe präzise abbilden und sich sauber weiterentwickeln lassen.",
      trigger: "Ein Standardmodul reicht nicht — der Prozess braucht eigene Logik oder eine Anbindung.",
      fit: "Individuelle Abläufe, Integrationen und Erweiterungen",
      foundation: "Odoo · Python · OCA-Standards",
      horizon: "Konzeption, Umsetzung und Weiterentwicklung",
      bodyTitle: "Erweiterungen mit einem klaren Platz im System",
      body: [
        "Am Anfang stehen die Fachbegriffe, Regeln und Datenflüsse des Prozesses. Wir ordnen die Anforderungen den passenden Odoo-Modulen zu und definieren klare Grenzen für eigene Erweiterungen.",
        "Module folgen den Konventionen der Odoo Community Association. Automatisierte Tests, nachvollziehbare Migrationen und dokumentierte Schnittstellen halten die Anwendung über Release-Wechsel hinweg verständlich.",
      ],
      deliverables: ["Individuelle Odoo-Module", "Schnittstellen zu Drittsystemen", "Automatisierte Tests und Migrationen", "Technische Dokumentation und Reviews"],
      quote: "Gute Odoo-Entwicklung übersetzt fachliche Regeln in Module, die Teams verstehen und langfristig pflegen können.",
      proofLinks: [["odoo", "Odoo im Überblick"], ["contact", "Entwicklungsvorhaben besprechen"]],
    },
    odooConsulting: {
      type: "detail",
      title: "Odoo-Beratung verbindet Prozesse und System.",
      context: "Leistungen · Odoo · Beratung",
      lede: "Wir klären Ziele, Prozesse und Verantwortlichkeiten und entwickeln daraus einen belastbaren Weg für Einführung oder Weiterentwicklung.",
      trigger: "Die Richtung ist offen: Reihenfolge, Aufwand und Risiko sind noch nicht abgeschätzt.",
      fit: "Einführungen, Erweiterungen und bestehende Odoo-Systeme",
      foundation: "Prozessanalyse · Modulkonzept · Odoo",
      horizon: "Vom Zielbild bis zur umsetzbaren Roadmap",
      bodyTitle: "Entscheidungen auf Grundlage der täglichen Arbeit",
      body: [
        "In Workshops erfassen wir Arbeitsabläufe, Rollen, Daten und Schnittstellen gemeinsam mit den beteiligten Teams. Daraus entsteht ein Zielbild mit nachvollziehbaren Prioritäten und Etappen.",
        "Bestehende Installationen prüfen wir anhand ihrer Module, Anpassungen, Datenqualität und Betriebswege. Die Ergebnisse werden als konkrete Entscheidungen, Risiken und nächste Schritte dokumentiert.",
      ],
      deliverables: ["Prozess- und Anforderungsworkshops", "Modul- und Einführungskonzept", "Analyse bestehender Installationen", "Priorisierte Roadmap und Aufwandseinschätzung"],
      quote: "Eine tragfähige Odoo-Entscheidung beginnt mit einem gemeinsamen Verständnis von Prozess, Verantwortung und Ziel.",
      proofLinks: [["odooDevelopment", "Odoo-Entwicklung"], ["contact", "Beratungsbedarf einordnen"]],
    },
    odooOperations: {
      type: "detail",
      title: "Odoo-Betrieb hält Anwendungen verlässlich verfügbar.",
      context: "Leistungen · Odoo · Betrieb",
      lede: "Wir planen Deployment, Überwachung, Backups und Updates als zusammenhängenden Betriebsweg für Ihre Odoo-Anwendung.",
      trigger: "Das System ist produktiv und muss verfügbar, gesichert und aktuell bleiben.",
      fit: "Produktive Odoo-Anwendungen mit verlässlichen Betriebsanforderungen",
      foundation: "Odoo · Linux · automatisierte Deployments",
      horizon: "Laufender Betrieb und vorbereitete Versionswechsel",
      bodyTitle: "Betrieb mit klaren Zuständigkeiten und überprüfbaren Wegen",
      body: [
        "Gemeinsam legen wir Umgebungen, Zugriffswege, Sicherungen, Überwachung und Wiederherstellung fest. Automatisierte Deployments sorgen dafür, dass Änderungen reproduzierbar in Test- und Produktivsysteme gelangen.",
        "Updates und Release-Wechsel werden früh geplant und unter realistischen Bedingungen geprüft. Status, Risiken und notwendige Entscheidungen bleiben für verantwortliche Personen transparent.",
      ],
      deliverables: ["Betriebs- und Deploymentkonzept", "Monitoring, Backups und Wiederherstellung", "Staging- und Produktivumgebungen", "Update- und Upgrade-Planung"],
      quote: "Verlässlicher Betrieb macht den Zustand einer Anwendung sichtbar und jeden notwendigen Eingriff nachvollziehbar.",
      proofLinks: [["maintenance", "Wartung über Release-Zyklen"], ["contact", "Betrieb besprechen"]],
    },
    plone: {
      type: "detail",
      title: "Plone für Inhalte mit Verantwortung.",
      context: "Leistungen · Plone",
      lede: "Wir bauen und modernisieren Plone-Anwendungen für Organisationen, die verlässliche Workflows, Berechtigungen und lange Wartungszeiträume benötigen.",
      fit: "Portale, Wissensplattformen und Intranets",
      foundation: "Plone · Python · offene Standards",
      horizon: "Konzeption, Migration und Pflege",
      bodyTitle: "Struktur für anspruchsvolle Inhalte",
      body: [
        "Plone verbindet ein ausgereiftes Inhaltsmodell mit fein steuerbaren Rollen und Arbeitsabläufen. Wir übersetzen fachliche Zuständigkeiten in eine Architektur, die Redaktionen sicher bedienen und Entwickler:innen sauber erweitern können.",
        "Bei bestehenden Installationen analysieren wir Erweiterungen, Inhalte und Betriebswege. Migrationen werden in überprüfbaren Schritten geplant, damit Redaktionen weiterarbeiten und Entscheidungen nachvollziehen können.",
      ],
      deliverables: ["Informationsarchitektur und Workflows", "Individuelle Inhaltstypen und Integrationen", "Barrierearme Benutzeroberflächen", "Upgrades und Migrationen"],
      childrenTitle: "Drei Einstiege, je nach Ausgangslage",
      children: ["ploneDevelopment", "ploneConsulting", "ploneOperations"],
      quote: "Unsere Plone-Werkzeuge werden upstream genutzt. Diese Nähe zur Community verbessert jede Kundenanwendung.",
      proofLinks: [["https://github.com/plone/plonecli", "plonecli auf GitHub"], ["https://github.com/plone/bobtemplates.plone", "bobtemplates.plone auf GitHub"]],
    },
    ploneDevelopment: {
      type: "detail",
      title: "Plone-Entwicklung entlang Ihrer Inhalte.",
      context: "Leistungen · Plone · Entwicklung",
      lede: "Wir entwickeln Inhaltstypen, Workflows und Add-ons, die redaktionelle Arbeit abbilden und den Weg zu künftigen Plone-Versionen offen halten.",
      trigger: "Redaktionen arbeiten an den Standardwerkzeugen vorbei, weil ihnen etwas Eigenes fehlt.",
      fit: "Eigene Inhaltstypen, Add-ons und Integrationen",
      foundation: "Plone · Python · Volto und klassische Oberfläche",
      horizon: "Konzeption, Umsetzung und Weiterentwicklung",
      bodyTitle: "Erweiterungen, die den Upgrade-Pfad offen halten",
      body: [
        "Am Anfang stehen die Inhalte selbst: welche Typen es gibt, wer sie pflegt und wie sie geprüft und veröffentlicht werden. Daraus entstehen Inhaltstypen, Verhalten und Arbeitsabläufe, die Redaktionen ohne Umwege bedienen können.",
        "Add-ons folgen den Konventionen der Plone-Community: versionierte Profile mit Upgrade-Schritten, automatisierte Tests und dokumentierte Schnittstellen. Die Oberfläche entsteht mit Volto oder der klassischen Oberfläche — je nachdem, was Redaktion und Betrieb dauerhaft tragen.",
      ],
      deliverables: ["Individuelle Inhaltstypen und Verhalten", "Add-ons mit Profilen und Upgrade-Schritten", "Blöcke, Views und barrierearme Oberflächen", "Automatisierte Tests und technische Dokumentation"],
      quote: "Eine Plone-Erweiterung ist dann gut gebaut, wenn das nächste Upgrade sie mitnehmen kann.",
      proofLinks: [["https://github.com/plone/plonecli", "plonecli auf GitHub"], ["plone", "Plone im Überblick"]],
    },
    ploneConsulting: {
      type: "detail",
      title: "Plone-Beratung ordnet Inhalte und Verantwortung.",
      context: "Leistungen · Plone · Beratung",
      lede: "Wir klären Informationsarchitektur, Rollen und Veröffentlichungswege und entwickeln daraus einen belastbaren Weg für Relaunch, Upgrade oder Neubau.",
      trigger: "Die Struktur ist über Jahre gewachsen und niemand kann sie mehr vollständig überblicken.",
      fit: "Relaunches, Upgrades und bestehende Plone-Installationen",
      foundation: "Informationsarchitektur · Rollen und Workflows · Plone",
      horizon: "Vom Zielbild bis zur umsetzbaren Roadmap",
      bodyTitle: "Entscheidungen, die Redaktionen mittragen",
      body: [
        "In Workshops erfassen wir Inhalte, Zuständigkeiten, Freigabewege und Schnittstellen gemeinsam mit Redaktion und IT. Daraus entsteht eine Informationsarchitektur mit Rollen und Arbeitsabläufen, die zur Organisation passt statt sie umzubauen.",
        "Bestehende Installationen prüfen wir anhand ihrer Add-ons, Anpassungen, Inhaltsmengen und Betriebswege. Das Ergebnis benennt den tragfähigen Weg zur aktuellen Plone-Version und die Stellen, die dabei besondere Aufmerksamkeit brauchen.",
      ],
      deliverables: ["Workshops zu Inhalten, Rollen und Abläufen", "Informationsarchitektur und Berechtigungskonzept", "Analyse bestehender Installationen und Add-ons", "Priorisierte Upgrade- oder Relaunch-Roadmap"],
      quote: "Eine Plone-Entscheidung trägt, wenn Redaktion, IT und Leitung dieselbe Landkarte vor sich haben.",
      proofLinks: [["ploneDevelopment", "Plone-Entwicklung"], ["contact", "Beratungsbedarf einordnen"]],
    },
    ploneOperations: {
      type: "detail",
      title: "Plone-Betrieb hält Redaktionen arbeitsfähig.",
      context: "Leistungen · Plone · Betrieb",
      lede: "Wir planen Deployment, Sicherungen, Überwachung und Sicherheitsupdates als zusammenhängenden Betriebsweg für Ihre Plone-Anwendung.",
      trigger: "Das Portal ist produktiv und darf auch bei Updates nicht stillstehen.",
      fit: "Produktive Portale, Intranets und Wissensplattformen",
      foundation: "Plone · Datenbank, Blobs und Suchindex · automatisierte Deployments",
      horizon: "Laufender Betrieb und vorbereitete Versionswechsel",
      bodyTitle: "Betrieb, der den Zustand sichtbar macht",
      body: [
        "Gemeinsam legen wir Umgebungen, Zugriffswege, Sicherungen und Wiederherstellung fest. Datenbank, Dateien und Suchindex gehören dabei zusammen: Eine Sicherung ist erst dann eine Sicherung, wenn die Wiederherstellung geprüft wurde.",
        "Sicherheitsupdates der Plone-Community werden zeitnah eingespielt, größere Versionswechsel früh vorbereitet und auf einer Kopie der echten Inhalte geprobt. Status, Risiken und notwendige Entscheidungen bleiben für verantwortliche Personen transparent.",
      ],
      deliverables: ["Betriebs- und Deploymentkonzept", "Sicherungen, Wiederherstellung und Monitoring", "Staging-Umgebung mit echten Inhalten", "Sicherheitsupdates und Upgrade-Planung"],
      quote: "Guter Betrieb fällt niemandem auf — außer an dem Tag, an dem eine Wiederherstellung gebraucht wird.",
      proofLinks: [["maintenance", "Wartung über Release-Zyklen"], ["contact", "Betrieb besprechen"]],
    },
    python: {
      type: "detail",
      title: "Python-Architektur passend zur Aufgabe.",
      context: "Leistungen · Django, Pyramid & FastAPI",
      lede: "Django, Pyramid und FastAPI decken unterschiedliche Aufgaben ab. Wir wählen die Grundlage nach Domäne, Team, Schnittstellen und erwarteter Lebensdauer.",
      fit: "Fachanwendungen, APIs und Integrationen",
      foundation: "Django · Pyramid · FastAPI",
      horizon: "Architektur, Entwicklung und Betrieb",
      bodyTitle: "Eine klare Domäne im Mittelpunkt",
      body: [
        "Am Anfang stehen Begriffe, Regeln und Abläufe der Fachdomäne. Darauf bauen Datenmodell, Schnittstellen und Benutzeroberfläche auf. Der gewählte Rahmen unterstützt diese Struktur und bleibt für das Team nachvollziehbar.",
        "Automatisierte Tests, reproduzierbare Deployments und dokumentierte Entscheidungen gehören zur Anwendung. So bleiben Änderungen beherrschbar, wenn Anforderungen, Team oder Infrastruktur wachsen.",
      ],
      deliverables: ["Domänen- und Systemarchitektur", "Webanwendungen und APIs", "Schnittstellen und Datenmigration", "Tests, Deployment und technische Dokumentation"],
      quote: "Bewährte Python-Werkzeuge geben uns die Freiheit, die Architektur an der Aufgabe auszurichten.",
      proofLinks: [["https://www.djangoproject.com/", "Django"], ["https://fastapi.tiangolo.com/", "FastAPI"], ["https://trypyramid.com/", "Pyramid"]],
    },
    sustainability: {
      type: "sustainability",
      title: "Nachhaltige Softwareentwicklung braucht Open Source.",
      heroTitle: "Nachhaltige Software&shy;entwicklung braucht Open Source.",
      context: "Nachhaltigkeit",
      lede: "Offene Software schützt Investitionen, ermöglicht Zusammenarbeit und erhält die Freiheit, eine Anwendung über viele Jahre weiterzuführen.",
      contactLead: "<strong>Wie handlungsfähig bleibt Ihre Software?</strong> Sie schildern uns Ihre Aufgabe. Wir klären gemeinsam, wie sich Quellcode, Daten und Wissen dauerhaft zugänglich halten lassen — und welcher nächste Schritt sinnvoll ist.",
    },
    care: {
      type: "overview",
      title: "Verantwortung über den Start hinaus.",
      context: "Support & Wartung",
      lede: "Betriebssicherheit wächst aus klaren Zuständigkeiten, kurzen Wegen und einer Wartung, die technische Entwicklungen früh einplant.",
      introTitle: "Zwei Aufgaben, ein verlässlicher Rahmen",
      intro: "Support löst konkrete Fragen im laufenden Betrieb. Wartung hält die technische Basis gesund. Beide Leistungen werden so kombiniert, wie Ihre Anwendung und Ihr Team sie benötigen.",
      children: ["support", "maintenance"],
    },
    support: {
      type: "detail",
      title: "Support mit direktem Weg zur Lösung.",
      context: "Support & Wartung · Support",
      lede: "Anfragen erreichen Menschen, die Ihre Anwendung, ihre Architektur und ihren Betrieb kennen. Das verkürzt die Analyse und macht Antworten belastbar.",
      fit: "Produktive Anwendungen und verantwortliche Teams",
      foundation: "Vereinbarte Wege und Zuständigkeiten",
      horizon: "Laufende Begleitung",
      bodyTitle: "Hilfe mit Kontext",
      body: [
        "Gemeinsam legen wir fest, wer Anfragen stellt, wie Dringlichkeit bewertet wird und welche Informationen die Analyse beschleunigen. Kritische Situationen erhalten einen klaren Eskalationsweg.",
        "Wiederkehrende Fragen fließen in Dokumentation, Schulung oder technische Verbesserungen ein. Support trägt dadurch zur Qualität der gesamten Anwendung bei.",
      ],
      deliverables: ["Definierte Kontakt- und Eskalationswege", "Nachvollziehbare Bearbeitung", "Analyse von Fehlern und Betriebsfragen", "Rückfluss in Dokumentation und Wartung"],
      quote: "Guter Support kennt den Unterschied zwischen einer schnellen Antwort und einer tragfähigen Lösung.",
      proofLinks: [["maintenance", "Wartung ergänzend planen"], ["contact", "Supportbedarf besprechen"]],
    },
    maintenance: {
      type: "detail",
      title: "Wartung hält Anwendungen beweglich.",
      context: "Support & Wartung · Wartung",
      lede: "Regelmäßige Updates, Sicherheitsarbeit und vorbereitete Versionswechsel erhalten die Handlungsfähigkeit Ihrer Anwendung.",
      fit: "Langfristig betriebene Geschäftsanwendungen",
      foundation: "Tests, Updates und Upgrade-Zyklen",
      horizon: "Planbar über Jahre",
      bodyTitle: "Technische Pflege mit Übersicht",
      body: [
        "Wir beobachten Abhängigkeiten, Sicherheitsmeldungen und Release-Zyklen. Notwendige Änderungen werden nach Risiko und Nutzen priorisiert und in einem gemeinsamen Wartungsplan sichtbar gemacht.",
        "Größere Upgrades werden früh vorbereitet. Automatisierte Tests und Staging-Umgebungen schaffen Sicherheit, bevor eine neue Version den produktiven Betrieb erreicht.",
      ],
      deliverables: ["Abhängigkeits- und Sicherheitsupdates", "Regelmäßige technische Zustandsberichte", "Test- und Staging-Strategie", "Geplante Versionswechsel und Migrationen"],
      quote: "Jedes gepflegte Release fügt der Anwendung einen weiteren gesunden Ring hinzu.",
      proofLinks: [["sustainability", "Unsere Nachhaltigkeitsprinzipien"], ["contact", "Wartungsbedarf einordnen"]],
    },
    knowledge: {
      type: "overview",
      title: "Wissen, das im Team weiterarbeitet.",
      context: "Schulungen & Vorträge",
      lede: "Wir vermitteln Zusammenhänge aus realen Projekten, geben erprobte Arbeitsweisen weiter und schaffen Raum für konkrete Fragen.",
      introTitle: "Lernen im passenden Format",
      intro: "Schulungen bearbeiten die Anwendung und das Team im Detail. Vorträge verdichten Erfahrungen zu einem klaren Thema und eröffnen die Diskussion.",
      children: ["training", "talks"],
    },
    training: {
      type: "training",
      title: "Schulungen für die nächste sichere Entscheidung.",
      context: "Schulungen & Vorträge · Schulungen",
      lede: "Von der kompakten Einführung bis zum mehrtägigen Teamformat: Inhalte, Übungen und Beispiele richten sich nach Vorkenntnissen und tatsächlicher Anwendung.",
    },
    talks: {
      type: "talks",
      title: "Vorträge aus gelebter Entwicklungspraxis.",
      context: "Schulungen & Vorträge · Vorträge",
      lede: "Konferenzbeiträge und buchbare Sessions zu Plone, Python, nachhaltiger Architektur und der Arbeit in Open-Source-Communities.",
    },
    contact: {
      type: "contact",
      title: "Erzählen Sie uns von Ihrer Anwendung.",
      context: "Kontakt",
      lede: "Ein erstes Gespräch ist kostenlos. Wir hören zu, ordnen die Aufgabe ein und benennen einen sinnvollen nächsten Schritt — auf Deutsch oder Englisch, remote oder in Neuhaus/Elbe.",
    },
    imprint: {
      type: "imprint",
      title: "Impressum",
      context: "Impressum",
      lede: "Angaben zum Anbieter dieser Website und Nachweise für verwendete Inhalte.",
    },
    styleguide: {
      type: "styleguide",
      title: "Styleguide für die Redaktion",
      heroTitle: "So sieht Text auf derico.de aus.",
      context: "Redaktion · Styleguide",
      lede: "Alle Textformate, Farben und Blockbreiten des Designs – mit den Namen, unter denen sie im Aurora-Editor zu finden sind.",
    },
  },
  en: {
    home: {
      type: "home",
      title: "Applications, grown to last.",
      context: "Sustainable solutions for more than 20 years",
      lede: "We develop business applications with Python, modern JavaScript and open source. Maintainability, open standards and clear decisions protect their value for years to come.",
    },
    services: {
      type: "overview",
      title: "Application development with a long horizon.",
      context: "Services",
      lede: "Technology carries its task when it fits the organisation, stays understandable and can be developed reliably.",
      introTitle: "Three proven foundations",
      intro: "We select frameworks according to process, organisation and expected lifetime. Architecture, interface and operations are planned as one connected task.",
      children: ["odoo", "plone", "python"],
    },
    odoo: {
      type: "detail",
      title: "Odoo connects your business processes.",
      context: "Services · Odoo",
      lede: "We introduce Odoo, develop modules to open OCA standards and keep the system ready for future releases.",
      fit: "Sales, purchasing, warehouse and invoicing",
      foundation: "Odoo · Python · OCA",
      horizon: "Introduction, modules and upgrades",
      bodyTitle: "A system that carries the real process",
      body: [
        "An Odoo introduction begins with the steps, responsibilities and data your team moves every day. This creates clear module boundaries and a rollout in useful stages.",
        "Custom extensions follow Odoo Community Association conventions. That improves testing, review and later upgrades. Documented decisions keep the application understandable as the team changes.",
      ],
      deliverables: ["Process and module concept", "OCA-compliant extensions", "Data migration and integrations", "Introduction, training and upgrade plan"],
      childrenTitle: "Three ways in, depending on where you stand",
      children: ["odooDevelopment", "odooConsulting", "odooOperations"],
      quote: "An ERP system carries its value when teams recognise their daily work and each extension has a clear place.",
      proofLinks: [["https://odoo-community.org/", "Odoo Community Association"], ["knowledge", "Training for your Odoo team"]],
    },
    odooDevelopment: {
      type: "detail",
      title: "Odoo development for clear processes.",
      context: "Services · Odoo · Development",
      lede: "We develop Odoo modules and integrations that represent business processes precisely and remain ready for continued development.",
      trigger: "A standard module isn't enough — the process needs its own logic or a connection.",
      fit: "Individual processes, integrations and extensions",
      foundation: "Odoo · Python · OCA standards",
      horizon: "Concept, implementation and continued development",
      bodyTitle: "Extensions with a clear place in the system",
      body: [
        "The work begins with the domain language, rules and data flows of the process. We map requirements to suitable Odoo modules and define clear boundaries for custom extensions.",
        "Modules follow Odoo Community Association conventions. Automated tests, traceable migrations and documented interfaces keep the application understandable across release changes.",
      ],
      deliverables: ["Custom Odoo modules", "Integrations with third-party systems", "Automated tests and migrations", "Technical documentation and reviews"],
      quote: "Good Odoo development translates domain rules into modules teams can understand and maintain over the long term.",
      proofLinks: [["odoo", "Odoo overview"], ["contact", "Discuss a development project"]],
    },
    odooConsulting: {
      type: "detail",
      title: "Odoo consulting connects processes and system.",
      context: "Services · Odoo · Consulting",
      lede: "We clarify goals, processes and responsibilities and turn them into a dependable path for introduction or continued development.",
      trigger: "The direction is still open: sequence, effort and risk have not been assessed.",
      fit: "Introductions, extensions and existing Odoo systems",
      foundation: "Process analysis · module concept · Odoo",
      horizon: "From target state to an actionable roadmap",
      bodyTitle: "Decisions grounded in daily work",
      body: [
        "In workshops, we capture processes, roles, data and integrations with the teams involved. The result is a target state with traceable priorities and delivery stages.",
        "We assess existing installations through their modules, customisations, data quality and operational paths. Findings become documented decisions, risks and concrete next steps.",
      ],
      deliverables: ["Process and requirements workshops", "Module and introduction concept", "Assessment of existing installations", "Prioritised roadmap and effort estimate"],
      quote: "A durable Odoo decision begins with a shared understanding of process, responsibility and purpose.",
      proofLinks: [["odooDevelopment", "Odoo development"], ["contact", "Discuss your consulting needs"]],
    },
    odooOperations: {
      type: "detail",
      title: "Odoo operations keep applications reliably available.",
      context: "Services · Odoo · Operations",
      lede: "We plan deployment, monitoring, backups and updates as one connected operational path for your Odoo application.",
      trigger: "The system is live and has to stay available, protected and current.",
      fit: "Production Odoo applications with dependable operational requirements",
      foundation: "Odoo · Linux · automated deployments",
      horizon: "Continuous operations and prepared release changes",
      bodyTitle: "Operations with clear ownership and verifiable paths",
      body: [
        "Together we define environments, access paths, backups, monitoring and recovery. Automated deployments move changes reproducibly into staging and production systems.",
        "Updates and release changes are planned early and tested under realistic conditions. Status, risks and required decisions remain transparent for responsible roles.",
      ],
      deliverables: ["Operations and deployment concept", "Monitoring, backups and recovery", "Staging and production environments", "Update and upgrade planning"],
      quote: "Dependable operations make an application's condition visible and every necessary intervention traceable.",
      proofLinks: [["maintenance", "Maintenance across release cycles"], ["contact", "Discuss operations"]],
    },
    plone: {
      type: "detail",
      title: "Plone for content with responsibility.",
      context: "Services · Plone",
      lede: "We build and modernise Plone applications for organisations that need dependable workflows, permissions and long maintenance horizons.",
      fit: "Portals, knowledge platforms and intranets",
      foundation: "Plone · Python · open standards",
      horizon: "Concept, migration and care",
      bodyTitle: "Structure for demanding content",
      body: [
        "Plone combines a mature content model with precise roles and workflows. We translate responsibilities into an architecture editors can use safely and developers can extend cleanly.",
        "For existing installations, we analyse extensions, content and operations. Migrations proceed in verifiable stages so editorial work can continue and decisions remain traceable.",
      ],
      deliverables: ["Information architecture and workflows", "Custom content types and integrations", "Accessible interfaces", "Upgrades and migrations"],
      childrenTitle: "Three ways in, depending on where you stand",
      children: ["ploneDevelopment", "ploneConsulting", "ploneOperations"],
      quote: "Our Plone tools are used upstream. That closeness to the community improves every client application.",
      proofLinks: [["https://github.com/plone/plonecli", "plonecli on GitHub"], ["https://github.com/plone/bobtemplates.plone", "bobtemplates.plone on GitHub"]],
    },
    ploneDevelopment: {
      type: "detail",
      title: "Plone development along your content.",
      context: "Services · Plone · Development",
      lede: "We develop content types, workflows and add-ons that represent editorial work and keep the path to future Plone releases open.",
      trigger: "Editors work around the standard tools because something of their own is missing.",
      fit: "Custom content types, add-ons and integrations",
      foundation: "Plone · Python · Volto and Classic UI",
      horizon: "Concept, implementation and continued development",
      bodyTitle: "Extensions that keep the upgrade path open",
      body: [
        "The work begins with the content itself: which types exist, who maintains them, and how they are reviewed and published. From that grow content types, behaviours and workflows editors can operate without detours.",
        "Add-ons follow Plone community conventions: versioned profiles with upgrade steps, automated tests and documented interfaces. The interface is built with Volto or the Classic UI — whichever the editorial team and operations can carry over the long term.",
      ],
      deliverables: ["Custom content types and behaviours", "Add-ons with profiles and upgrade steps", "Blocks, views and accessible interfaces", "Automated tests and technical documentation"],
      quote: "A Plone extension is well built when the next upgrade can bring it along.",
      proofLinks: [["https://github.com/plone/plonecli", "plonecli on GitHub"], ["plone", "Plone overview"]],
    },
    ploneConsulting: {
      type: "detail",
      title: "Plone consulting orders content and responsibility.",
      context: "Services · Plone · Consulting",
      lede: "We clarify information architecture, roles and publication paths and turn them into a dependable route for a relaunch, an upgrade or a new build.",
      trigger: "The structure has grown over years and no one can take it all in any more.",
      fit: "Relaunches, upgrades and existing Plone installations",
      foundation: "Information architecture · roles and workflows · Plone",
      horizon: "From target state to an actionable roadmap",
      bodyTitle: "Decisions the editorial team can carry",
      body: [
        "In workshops, we capture content, responsibilities, approval paths and integrations together with editors and IT. The result is an information architecture with roles and workflows that fit the organisation instead of rebuilding it.",
        "We assess existing installations through their add-ons, customisations, content volume and operational paths. The findings name the viable route to the current Plone release and the places that will need particular attention.",
      ],
      deliverables: ["Workshops on content, roles and processes", "Information architecture and permission concept", "Assessment of existing installations and add-ons", "Prioritised upgrade or relaunch roadmap"],
      quote: "A Plone decision carries when editors, IT and management are looking at the same map.",
      proofLinks: [["ploneDevelopment", "Plone development"], ["contact", "Discuss your consulting needs"]],
    },
    ploneOperations: {
      type: "detail",
      title: "Plone operations keep editorial teams working.",
      context: "Services · Plone · Operations",
      lede: "We plan deployment, backups, monitoring and security updates as one connected operational path for your Plone application.",
      trigger: "The portal is live and must not stall, not even during updates.",
      fit: "Production portals, intranets and knowledge platforms",
      foundation: "Plone · database, files and search index · automated deployments",
      horizon: "Continuous operations and prepared release changes",
      bodyTitle: "Operations that make the state visible",
      body: [
        "Together we define environments, access paths, backups and recovery. Database, files and search index belong together: a backup only becomes a backup once the restore has been verified.",
        "Security updates from the Plone community are applied promptly, larger release changes are prepared early and rehearsed against a copy of the real content. Status, risks and required decisions remain transparent for responsible roles.",
      ],
      deliverables: ["Operations and deployment concept", "Backups, recovery and monitoring", "Staging environment with real content", "Security updates and upgrade planning"],
      quote: "Good operations go unnoticed — except on the day a restore is needed.",
      proofLinks: [["maintenance", "Maintenance across release cycles"], ["contact", "Discuss operations"]],
    },
    python: {
      type: "detail",
      title: "Python architecture fitted to the task.",
      context: "Services · Django, Pyramid & FastAPI",
      lede: "Django, Pyramid and FastAPI address different needs. We choose the foundation around domain, team, integrations and expected lifetime.",
      fit: "Business applications, APIs and integrations",
      foundation: "Django · Pyramid · FastAPI",
      horizon: "Architecture, development and operations",
      bodyTitle: "A clear domain at the centre",
      body: [
        "The work starts with the terms, rules and processes of the domain. Data, interfaces and user experience grow from that model. The selected framework supports the structure and stays readable for the team.",
        "Automated tests, reproducible deployment and documented decisions belong to the application. Change remains manageable as requirements, team and infrastructure grow.",
      ],
      deliverables: ["Domain and system architecture", "Web applications and APIs", "Integrations and data migration", "Tests, deployment and technical documentation"],
      quote: "Proven Python tools let us align architecture with the real task.",
      proofLinks: [["https://www.djangoproject.com/", "Django"], ["https://fastapi.tiangolo.com/", "FastAPI"], ["https://trypyramid.com/", "Pyramid"]],
    },
    sustainability: {
      type: "sustainability",
      title: "Sustainable software development needs open source.",
      context: "Sustainability",
      lede: "Open software protects investments, enables collaboration and preserves the freedom to keep an application going for many years.",
      contactLead: "<strong>How much room to act does your software leave you?</strong> Tell us about your task. Together we work out how source code, data and knowledge can stay accessible for the long term — and which next step makes sense.",
    },
    care: {
      type: "overview",
      title: "Responsibility beyond launch.",
      context: "Support & maintenance",
      lede: "Operational confidence grows from clear ownership, short paths and maintenance that plans technical change early.",
      introTitle: "Two tasks, one dependable framework",
      intro: "Support resolves concrete questions in daily operation. Maintenance keeps the technical foundation healthy. We combine both around your application and team.",
      children: ["support", "maintenance"],
    },
    support: {
      type: "detail",
      title: "Support with a direct path to resolution.",
      context: "Support & maintenance · Support",
      lede: "Requests reach people who know your application, architecture and operations. Analysis becomes faster and answers become more reliable.",
      fit: "Production applications and responsible teams",
      foundation: "Agreed paths and ownership",
      horizon: "Continuous guidance",
      bodyTitle: "Help with context",
      body: [
        "Together we define who raises requests, how urgency is assessed and which information speeds analysis. Critical situations receive a clear escalation path.",
        "Recurring questions feed documentation, training or technical improvements. Support therefore contributes to the quality of the whole application.",
      ],
      deliverables: ["Defined contact and escalation paths", "Traceable handling", "Analysis of faults and operational questions", "Feedback into documentation and maintenance"],
      quote: "Good support understands the difference between a quick answer and a durable resolution.",
      proofLinks: [["maintenance", "Plan complementary maintenance"], ["contact", "Discuss your support needs"]],
    },
    maintenance: {
      type: "detail",
      title: "Maintenance keeps applications adaptable.",
      context: "Support & maintenance · Maintenance",
      lede: "Regular updates, security work and prepared release changes preserve your application's ability to move.",
      fit: "Long-running business applications",
      foundation: "Tests, updates and upgrade cycles",
      horizon: "Predictable across years",
      bodyTitle: "Technical care with visibility",
      body: [
        "We monitor dependencies, security notices and release cycles. Necessary changes are prioritised by risk and value and remain visible in a shared maintenance plan.",
        "Larger upgrades are prepared early. Automated tests and staging environments create confidence before a new release reaches production.",
      ],
      deliverables: ["Dependency and security updates", "Regular technical health reports", "Test and staging strategy", "Planned upgrades and migrations"],
      quote: "Every maintained release adds another healthy ring to the application.",
      proofLinks: [["sustainability", "Our sustainability principles"], ["contact", "Assess your maintenance needs"]],
    },
    knowledge: {
      type: "overview",
      title: "Knowledge that keeps working in the team.",
      context: "Training & talks",
      lede: "We share connections from real projects, pass on proven practices and create room for specific questions.",
      introTitle: "Learning in the right format",
      intro: "Training explores the application and team in detail. Talks focus experience into a clear subject and open the discussion.",
      children: ["training", "talks"],
    },
    training: {
      type: "training",
      title: "Training for the next confident decision.",
      context: "Training & talks · Training",
      lede: "From a focused introduction to a multi-day team format: content, exercises and examples reflect existing knowledge and the real application.",
    },
    talks: {
      type: "talks",
      title: "Talks grounded in development practice.",
      context: "Training & talks · Talks",
      lede: "Conference contributions and bookable sessions on Plone, Python, sustainable architecture and work in open-source communities.",
    },
    contact: {
      type: "contact",
      title: "Tell us about your application.",
      context: "Contact",
      lede: "An initial conversation is free. We listen, assess the task and identify a useful next step — in German or English, remotely or in Neuhaus/Elbe.",
    },
    imprint: {
      type: "imprint",
      title: "Legal notice",
      context: "Legal notice",
      lede: "Provider information for this website and credits for licensed content.",
    },
    styleguide: {
      type: "styleguide",
      title: "Editorial style guide",
      heroTitle: "This is what text looks like on derico.de.",
      context: "Editorial · Style guide",
      lede: "Every text format, colour and block width of the design, under the names the Aurora editor uses for them.",
    },
  },
};

const groupFor = (key) => {
  if (["services", "odoo", "odooDevelopment", "odooConsulting", "odooOperations", "plone", "ploneDevelopment", "ploneConsulting", "ploneOperations", "python"].includes(key)) return "services";
  if (["care", "support", "maintenance"].includes(key)) return "care";
  if (["knowledge", "training", "talks"].includes(key)) return "knowledge";
  return null;
};

const href = (lang, key) => slugs[lang][key];
const resolvedHref = (lang, value) => (slugs[lang][value] ? href(lang, value) : value);

function megaPanel(lang, name, current) {
  const item = navigation[lang][name];
  return `<div class="mega-panel" id="mega-${name}" data-mega-panel hidden>
    <div class="mega-inner">
      <div class="mega-intro">
        <h2><a href="${href(lang, name)}">${item.label}</a></h2>
        <p>${item.intro}</p>
        <a class="mega-overview" href="${href(lang, name)}">${item.overview}</a>
      </div>
      <ul class="mega-links">
        ${item.links.map(([key, title, text, children = []]) => `<li><a href="${href(lang, key)}"${current === key ? ' aria-current="page"' : ""}><span><strong>${title}</strong><span>${text}</span></span></a>${children.length ? `<ul class="mega-sublinks" aria-label="${title}">${children.map(([childKey, childTitle]) => `<li><a href="${href(lang, childKey)}"${current === childKey ? ' aria-current="page"' : ""}>${childTitle}</a></li>`).join("")}</ul>` : ""}</li>`).join("")}
      </ul>
      <p class="mega-proof">${item.proof}</p>
    </div>
  </div>`;
}

function header(lang, current) {
  const nav = navigation[lang];
  const group = groupFor(current);
  const currentAttr = (key) => (current === key ? ' aria-current="page"' : "");
  const groupClass = (key) => (group === key ? " is-current" : "");
  return `<a class="skip-link" href="#main">${nav.skip}</a>
  <header class="site-header" data-site-header data-nav-open="false">
    <div class="header-shell shell">
      <a class="brand-mark" href="${href(lang, "home")}" aria-label="${nav.homeLabel}">
        <img src="../assets/derico-logo.svg" alt="" width="423" height="146">
      </a>
      <button class="menu-toggle" type="button" data-menu-toggle aria-controls="site-navigation" aria-expanded="false">
        <span class="menu-toggle__icon" aria-hidden="true"></span><span>${nav.menu}</span>
      </button>
      <nav class="site-nav" id="site-navigation" aria-label="${lang === "de" ? "Hauptnavigation" : "Primary navigation"}">
        <ul class="primary-nav">
          <li>
            <button class="nav-trigger${groupClass("services")}" type="button" data-mega-trigger aria-expanded="false" aria-controls="mega-services">${nav.services.label}</button>
            ${megaPanel(lang, "services", current)}
          </li>
          <li><a class="nav-link" href="${href(lang, "sustainability")}"${currentAttr("sustainability")}>${nav.sustainability}</a></li>
          <li>
            <button class="nav-trigger${groupClass("care")}" type="button" data-mega-trigger aria-expanded="false" aria-controls="mega-care">${nav.care.label}</button>
            ${megaPanel(lang, "care", current)}
          </li>
          <li>
            <button class="nav-trigger${groupClass("knowledge")}" type="button" data-mega-trigger aria-expanded="false" aria-controls="mega-knowledge">${nav.knowledge.label}</button>
            ${megaPanel(lang, "knowledge", current)}
          </li>
          <li><a class="nav-link" href="${href(lang, "contact")}"${currentAttr("contact")}>${nav.contact}</a></li>
        </ul>
      </nav>
      <div class="header-utility">
        <ul class="utility-nav" aria-label="${lang === "de" ? "Sprachauswahl" : "Language selection"}">
          <li><a href="../de/${slugs.de[current]}"${lang === "de" ? ' aria-current="page"' : ""} lang="de">DE</a></li>
          <li aria-hidden="true">/</li>
          <li><a href="../en/${slugs.en[current]}"${lang === "en" ? ' aria-current="page"' : ""} lang="en">EN</a></li>
        </ul>
        <div class="site-search" data-site-search data-search-open="false">
          <button class="search-toggle" type="button" data-search-toggle aria-controls="site-search-form" aria-expanded="false" data-label-open="${nav.searchOpen}" data-label-close="${nav.searchClose}">
            <svg class="search-toggle__glyph search-toggle__glyph--open" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.6-4.6"/></svg>
            <svg class="search-toggle__glyph search-toggle__glyph--close" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"/></svg>
            <span class="visually-hidden" data-search-label>${nav.searchOpen}</span>
          </button>
          <form class="site-search__form" id="site-search-form" role="search" action="#" hidden>
            <label class="visually-hidden" for="site-search-field">${nav.searchField}</label>
            <input class="site-search__field" id="site-search-field" type="search" name="q" placeholder="${nav.searchField}" autocomplete="off" spellcheck="false">
            <button class="site-search__submit" type="submit">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m20 20-4.6-4.6"/></svg>
              <span class="visually-hidden">${nav.searchSubmit}</span>
            </button>
          </form>
        </div>
      </div>
    </div>
    <button class="mega-backdrop" type="button" data-mega-backdrop hidden aria-label="${lang === "de" ? "Menü schließen" : "Close menu"}"></button>
  </header>`;
}

function breadcrumbs(lang, key, label) {
  if (key === "home") return "";
  const home = lang === "de" ? "Startseite" : "Home";
  const group = groupFor(key);
  const groupLabel = group ? navigation[lang][group].label : null;
  const groupCrumb = group && group !== key ? `<li><a href="${href(lang, group)}">${groupLabel}</a></li>` : "";
  const parents = {
    odooDevelopment: ["odoo", "Odoo"], odooConsulting: ["odoo", "Odoo"], odooOperations: ["odoo", "Odoo"],
    ploneDevelopment: ["plone", "Plone"], ploneConsulting: ["plone", "Plone"], ploneOperations: ["plone", "Plone"],
  };
  const parent = parents[key];
  const parentCrumb = parent ? `<li><a href="${href(lang, parent[0])}">${parent[1]}</a></li>` : "";
  return `<nav class="breadcrumbs" aria-label="${lang === "de" ? "Brotkrümelnavigation" : "Breadcrumb"}"><div class="shell"><ol><li><a href="${href(lang, "home")}">${home}</a></li>${groupCrumb}${parentCrumb}<li aria-current="page">${label}</li></ol></div></nav>`;
}

function footer(lang) {
  const nav = navigation[lang];
  return `<footer class="site-footer"><div class="shell footer-grid">
    <div><p><strong>derico</strong> · ${nav.footerLine}</p><p>Maik Derstappen · Laaver Weg 2 · 19273 Neuhaus/Elbe</p></div>
    <ul class="footer-links"><li><a href="tel:+491788612833">+49 178 861 2 833</a></li><li><a href="mailto:md@derico.de">md@derico.de</a></li><li><a href="${href(lang, "imprint")}">${nav.imprint}</a></li></ul>
  </div></footer>`;
}

function rings(lang) {
  const labels = lang === "de"
    ? [["schneller Prototyp", "in Wochen bedienbar"], ["erste Anwendung", "trägt die tägliche Arbeit"], ["erfahrener Begleiter", "wächst mit den Anforderungen"], ["mit der Zeit gegangen", "offen, aktuell, migrierbar"]]
    : [["rapid prototype", "usable within weeks"], ["first application", "supports daily work"], ["experienced companion", "grows with requirements"], ["kept current", "open, maintained, portable"]];
  return `<figure class="rings-figure">
    <div class="rings-stage">
      <svg class="rings-disc" viewBox="0 0 680 470" role="img" aria-label="${lang === "de" ? "Wachstumsringe einer Anwendung" : "Growth rings of an application"}">
        <g transform="translate(105 0)" class="ring-halo">
          <circle cx="150" cy="235" r="40" class="ring-thin"/>
          <circle cx="153" cy="232" r="80"/>
          <circle cx="147" cy="238" r="125" class="ring-thin"/>
          <circle cx="154" cy="231" r="170"/>
          <circle cx="148" cy="237" r="215" class="ring-thin"/>
          <circle cx="152" cy="234" r="250"/>
          <circle cx="150" cy="235" r="290" class="ring-now"/>
          <circle cx="151" cy="234" r="315" class="ring-future"/>
        </g>
        <g transform="translate(105 0)" class="ring-ink">
          <circle cx="150" cy="235" r="40" class="ring-thin"/>
          <circle cx="153" cy="232" r="80"/>
          <circle cx="147" cy="238" r="125" class="ring-thin"/>
          <circle cx="154" cy="231" r="170"/>
          <circle cx="148" cy="237" r="215" class="ring-thin"/>
          <circle cx="152" cy="234" r="250"/>
          <circle cx="150" cy="235" r="290" class="ring-now"/>
          <circle cx="151" cy="234" r="315" class="ring-future"/>
        </g>
      </svg>
      <ol class="ring-markers" aria-hidden="true"><li>1</li><li>2</li><li>3</li><li class="is-now">4</li></ol>
    </div>
    <dl class="ring-legend">${labels.map(([title, text], index) => `<div${index === 3 ? ' class="is-now"' : ""}><b>${index + 1}</b><dt>${title}</dt><dd>${text}</dd></div>`).join("")}</dl>
  </figure>`;
}

function pageHero(page) {
  return `<section class="page-hero"><div class="shell page-hero__grid"><div><p class="page-context">${page.context}</p><h1>${page.heroTitle ?? page.title}</h1></div><p class="lede">${page.lede}</p></div></section>`;
}

function contactBand(lang, page) {
  const nav = navigation[lang];
  const lead = page.contactLead ?? nav.contactLead;
  return `<section class="contact-band"><div class="shell"><h2>${nav.firstTalk}</h2><p>${lead}</p><div class="action-row"><a class="button" href="${href(lang, "contact")}">${nav.contact}</a><a class="quiet-link" href="mailto:md@derico.de">${nav.email}</a></div></div></section>`;
}

function heroMedia() {
  return `<picture class="hero-media" aria-hidden="true">
    <source media="(max-width: 55.99rem)" type="image/avif" srcset="../assets/images/hero-managed-forest-portrait-720.avif 720w, ../assets/images/hero-managed-forest-portrait-1080.avif 1080w" sizes="100vw">
    <source media="(max-width: 55.99rem)" type="image/webp" srcset="../assets/images/hero-managed-forest-portrait-720.webp 720w, ../assets/images/hero-managed-forest-portrait-1080.webp 1080w" sizes="100vw">
    <source type="image/avif" srcset="../assets/images/hero-managed-forest-wide-960.avif 960w, ../assets/images/hero-managed-forest-wide-1600.avif 1600w, ../assets/images/hero-managed-forest-wide-2400.avif 2400w" sizes="100vw">
    <source type="image/webp" srcset="../assets/images/hero-managed-forest-wide-960.webp 960w, ../assets/images/hero-managed-forest-wide-1600.webp 1600w, ../assets/images/hero-managed-forest-wide-2400.webp 2400w" sizes="100vw">
    <source media="(max-width: 55.99rem)" type="image/jpeg" srcset="../assets/images/hero-managed-forest-portrait-720.jpg 720w, ../assets/images/hero-managed-forest-portrait-1080.jpg 1080w" sizes="100vw">
    <img src="../assets/images/hero-managed-forest-wide-1600.jpg" srcset="../assets/images/hero-managed-forest-wide-960.jpg 960w, ../assets/images/hero-managed-forest-wide-1600.jpg 1600w, ../assets/images/hero-managed-forest-wide-2400.jpg 2400w" sizes="100vw" width="2400" height="1200" alt="" fetchpriority="high" decoding="async">
  </picture><div class="hero-wash" aria-hidden="true"></div>`;
}

// Balkenlage — the floor-beam layer of a Hallenhaus, drawn in section: a Dielen
// (floorboard) layer seen edge-on, with the Deckenbalken hanging beneath it at
// a regular Achsmaß. It divides content into two storeys and is the one timber
// element that may be placed freely; the Ständerwerk below stays reserved.
//
// The cut runs through the beams, not through their joints, so there are no
// Zapfen here and no copper: a peg in a section this far from the Rähm would be
// a drawing error, and a page-wide row of copper would spend the accent the CTA
// needs. What a cut beam does show is its end grain — Jahresringe, the same
// figure the hero disc draws, arriving here as a property of the material.
//
// Each Balkenkopf is cut from a different part of the log: some carry a visible
// Mark with closed rings around it, others only the sweep of rings whose centre
// lies outside the beam. Four cuts, cycled on an uneven period, so no two
// neighbours match and the row never reads as a stamped repeat.
// Every radius is measured against the beam's corners, not guessed: the rings
// have to span the distance from the nearest corner to the furthest one, or the
// arcs bunch into one corner and leave the rest of the face blank — which reads
// as an unfinished drawing rather than as timber cut off the log's centre.
const balkenCuts = [
  // Mark low and left of centre; the outer rings run off two edges.
  `<circle cx="16" cy="20" r="1.4" class="balken-mark"/>
          <circle cx="16" cy="20" r="4"/>
          <circle cx="16" cy="20" r="10"/>
          <circle cx="16" cy="20" r="19"/>
          <circle cx="16" cy="20" r="30"/>`,
  // Cut from well outside the log's centre: arcs sweeping the whole face.
  `<circle cx="-10" cy="40" r="24"/>
          <circle cx="-10" cy="40" r="40"/>
          <circle cx="-10" cy="40" r="58"/>`,
  // Mark high and right, rings running off the top corner.
  `<circle cx="38" cy="8" r="1.4" class="balken-mark"/>
          <circle cx="38" cy="8" r="4"/>
          <circle cx="38" cy="8" r="9"/>
          <circle cx="38" cy="8" r="17"/>
          <circle cx="38" cy="8" r="28"/>`,
  // Centre far off to the side: near-vertical rings, a plank cut of the log.
  `<circle cx="74" cy="14" r="32"/>
          <circle cx="74" cy="14" r="45"/>
          <circle cx="74" cy="14" r="60"/>`,
];

// Twelve beams is one more than the widest shell can place at the smallest
// Achsmaß; the grid shows whole bays only and hides the remainder, so the row
// gains and loses beams the way a building gains bays. The cut order and the
// Dielenstöße are fixed here rather than derived from an nth-child rule: a
// mechanical every-third-beam pattern is exactly what irregular timber isn't.
const balkenOrder = [0, 1, 2, 1, 3, 0, 2, 3];
// Uneven gaps, and never the middle beam of an odd row — a Stoß landing dead
// centre is the one position that reads as placed rather than as where the
// boards happened to end.
const balkenStoss = new Set([2, 6]);

function balkenkopf(index) {
  const stoss = balkenStoss.has(index + 1) ? ' data-stoss=""' : "";
  // The rings live in a nested <svg>, whose viewport clips them to the beam's
  // inside face. A nested viewport does what a <clipPath> would without minting
  // an id that has to stay unique across every divider on the page.
  // The beams lie flat: the cut end is clearly wider than it is tall. Square it
  // up and the row reads as a strip of tiles rather than as timber.
  return `<span class="balkenlage__balken" style="--i:${index}"${stoss}>
          <svg viewBox="0 0 52 28" aria-hidden="true" focusable="false">
            <rect class="balken-body" x="0.75" y="0.75" width="50.5" height="26.5"/>
            <svg x="1.5" y="1.5" width="49" height="25" viewBox="1.5 1.5 49 25">
              <g class="balken-ringe">${balkenCuts[balkenOrder[index]]}</g>
            </svg>
          </svg>
        </span>`;
}

function balkenlage() {
  return `<div class="balkenlage" data-balkenlage aria-hidden="true">
        <span class="balkenlage__dielen"></span>
        <span class="balkenlage__lage">${balkenOrder.map((_, i) => balkenkopf(i)).join("")}</span>
      </div>`;
}

// Niederdeutsches Ständerwerk underpinning Support & Wartung: a Schwelle (sill
// beam) carrying two Gebinde (post-and-brace assemblies), pegged with Zapfen.
// Open at the top — no Rähm — so it reads as a standing frame, not a building.
//
// Real timber has width, so the members are drawn beams, not lines: outlined at
// the brand's own stroke weight, with Maserung (grain) and an Ast (knot) to say
// wood without reaching for a brown the palette does not have. Thick beams need
// true carpentry joints, so each corner Gebinde is one fixed-size SVG whose
// Fußband abuts post and sill on properly cut ends; only the Schwelle between
// them stretches, and a sill is the one member that can stretch honestly.
function serviceGebinde(side) {
  // Ständer 40 units on 174 of length, Fußband 32 thick — roughly 4:1, the squat
  // proportion of real sawn timber rather than a stroked line. The Fußband's
  // ends are cut square against post and sill so the joint closes the way a
  // carpenter would cut it. One line of grain and one Ast per beam: enough to
  // read as wood, few enough to stay a drawing.
  return `<svg class="service-frame__gebinde service-frame__gebinde--${side}" viewBox="0 0 210 190" aria-hidden="true" focusable="false">
        <g class="frame-beam">
          <path d="M20 16h40v174H20Z"/>
          <path d="M60 62 188 190h-45L60 107Z"/>
        </g>
        <g class="frame-grain">
          <path d="M20 24h40"/>
          <path d="M32 30c3 44-2 90 1 152"/>
          <path d="M82 104 160 182"/>
        </g>
        <g class="frame-ast">
          <ellipse cx="48" cy="120" rx="5" ry="6.8"/>
          <ellipse cx="48" cy="120" rx="1.9" ry="2.6"/>
        </g>
        <g class="frame-zapfen">
          <circle cx="40" cy="85" r="7"/>
          <circle cx="40" cy="168" r="7"/>
        </g>
      </svg>`;
}

function serviceFrame() {
  return `<span class="service-frame" data-service-frame aria-hidden="true">
        <span class="service-frame__schwelle"></span>
        ${serviceGebinde("start")}
        ${serviceGebinde("end")}
      </span>`;
}

function guideGraphic(lang, subject, className) {
  return `<img class="${className}" src="../assets/images/${subject}_${lang}.png" width="1254" height="1254" alt="" loading="lazy" decoding="async">`;
}

function renderServiceGuide(lang) {
  const isDe = lang === "de";
  const copy = isDe ? {
    heading: "Ein Bestimmungsbuch unserer Arbeit.",
    intro: "Zwei Plattformen, spezialisierte Frameworks und eine Betreuung, die Anwendungen über ihren gesamten Lebenszyklus begleitet.",
    action: "Mehr erfahren",
    odooPurpose: "Geschäftsanwendungen",
    odooText: "Geschäftsanwendungen für verbundene Prozesse – von Vertrieb und Einkauf bis Lager und Abrechnung.",
    plonePurpose: "Sichere Inhaltsplattformen",
    ploneText: "Sichere Inhaltsplattformen für Redaktionen, Gruppen, Workflows und fein abgestufte Berechtigungen.",
    frameworksTitle: "Spezialisierte Frameworks",
    frameworksPurpose: "Fokussiert auf die konkrete Aufgabe",
    frameworksText: "Mit Django, Pyramid, FastAPI und SvelteKit entwickeln wir fokussierte Anwendungen für spezialisierte Anforderungen.",
    careTitle: "Support & Wartung",
    carePurpose: "Begleitung über den gesamten Lebenszyklus",
    careText: "Support, Updates und Migration für Anwendungen im täglichen Betrieb.",
  } : {
    heading: "A field guide to our work.",
    intro: "Two platforms, specialised frameworks and dependable care across the complete application lifecycle.",
    action: "Learn more",
    odooPurpose: "Business applications",
    odooText: "Business applications for connected processes, from sales and purchasing to inventory and accounting.",
    plonePurpose: "Secure content platforms",
    ploneText: "Secure content platforms for editorial teams, groups, workflows and finely controlled permissions.",
    frameworksTitle: "Specialised frameworks",
    frameworksPurpose: "Focused on the task at hand",
    frameworksText: "We use Django, Pyramid, FastAPI and SvelteKit to build focused applications for specialised requirements.",
    careTitle: "Support & maintenance",
    carePurpose: "Care across the complete lifecycle",
    careText: "Support, updates and migration for applications in daily operation.",
  };
  const action = `<span class="service-action">${copy.action}<span aria-hidden="true">→</span></span>`;
  return `<section class="section services-guide-section" aria-labelledby="services-guide-title"><div class="shell">
    <div class="services-guide-header"><h2 class="section-heading" id="services-guide-title">${copy.heading}</h2><p class="section-intro">${copy.intro}</p></div>
    <div class="service-atlas">
      <div class="service-platforms">
        <a class="service-node service-platform service-platform--odoo" href="${href(lang, "odoo")}">
          <span class="service-platform__disc">${guideGraphic(lang, "odoo", "service-platform-graphic")}<h3 class="visually-hidden">Odoo · ${copy.odooPurpose}</h3></span>
          <span class="service-copy">${copy.odooText}</span>${action}
        </a>
        <a class="service-node service-platform service-platform--plone" href="${href(lang, "plone")}">
          <span class="service-platform__disc">${guideGraphic(lang, "plone", "service-platform-graphic")}<h3 class="visually-hidden">Plone · ${copy.plonePurpose}</h3></span>
          <span class="service-copy">${copy.ploneText}</span>${action}
        </a>
      </div>
      ${balkenlage()}
      <a class="service-node service-frameworks" href="${href(lang, "python")}">
        ${guideGraphic(lang, "frameworks", "service-frameworks-graphic")}
        <h3 class="visually-hidden">${copy.frameworksTitle}</h3><span class="visually-hidden">${copy.frameworksPurpose}. Django, Pyramid, FastAPI, SvelteKit. ${copy.frameworksText}</span>${action}
      </a>
      <a class="service-node service-care" href="${href(lang, "care")}">
        ${serviceFrame()}
        <span class="service-care__content"><span class="service-purpose">${copy.carePurpose}</span><h3>${copy.careTitle}</h3><span class="service-copy">${copy.careText}</span>${action}</span>
      </a>
    </div>
  </div></section>`;
}

function renderHome(lang, page) {
  const nav = navigation[lang];
  const manifesto = lang === "de" ? [
    ["Solide und durchdacht", "Bewährte Frameworks, wenige Abhängigkeiten und dokumentierte Entscheidungen schaffen Anwendungen, die im Alltag zuverlässig funktionieren."],
    ["Arbeit wird spürbar leichter", "Unsere Lösungen unterstützen Teams in ihren Abläufen und erhöhen die Produktivität und Qualität der Ergebnisse."],
    ["Offene Standards sichern den Wert", "Open Source und offene Schnittstellen halten Systeme zugänglich, erweiterbar und übertragbar."],
    ["Pflege ist Teil der Architektur", "Updates, Sicherheitsarbeit und Migration werden früh mitgedacht und über Jahre planbar gemacht."],
  ] : [
    ["Solid and considered", "Proven frameworks, limited dependencies and documented decisions create applications that work reliably in daily use."],
    ["Work becomes noticeably easier", "Our solutions support teams in their processes and improve productivity and the quality of their results."],
    ["Open standards protect value", "Open source and open interfaces keep systems accessible, extensible and transferable."],
    ["Care belongs in the architecture", "Updates, security work and migration are planned early and made predictable across years."],
  ];
  return `<section class="home-hero">${heroMedia()}<div class="shell home-hero__grid"><div><p class="kicker">${page.context}</p><h1>${page.title}</h1><p class="lede">${page.lede}</p><div class="action-row"><a class="button" href="${href(lang, "contact")}">${nav.firstTalk}</a><a class="quiet-link" href="${href(lang, "services")}">${nav.services.overview}</a></div></div>${rings(lang)}</div></section>
  <section class="section section--band"><div class="shell"><h2 class="section-heading">${lang === "de" ? "Nachhaltige Anwendungen sind eine Investition, die trägt." : "Sustainable applications are investments that keep delivering."}</h2><div class="manifesto-grid">${manifesto.map(([title, text]) => `<article class="manifesto-item"><h3>${title}</h3><p>${text}</p></article>`).join("")}</div></div></section>
  ${renderServiceGuide(lang)}`;
}

function childLabel(lang, key) {
  return pages[lang][key].context.split(" · ").at(-1);
}

// Overview pages: the children ARE the page body, so here they are only named.
// Their description is said once, at the tail, by subnav().
function pillarLine(lang, children) {
  return `<ul class="pillar-line">${children.map((key) => `<li><a href="${href(lang, key)}">${childLabel(lang, key)}</a></li>`).join("")}</ul>`;
}

// Detail pages: the children are keyed to the READER'S situation ("das System
// ist produktiv…"), never to what we do — that sentence belongs to subnav(),
// and saying it twice on one page was the whole problem this split solves.
function triage(lang, children) {
  return `<dl class="triage">${children.map((key) => `<div class="triage__row"><dt><a href="${href(lang, key)}">${childLabel(lang, key)}</a></dt><dd>${pages[lang][key].trigger}</dd></div>`).join("")}</dl>`;
}

// The page-tail sub-navigation. Chrome, not content: it sits OUTSIDE <main>,
// between the page body and the contact band, so this file matches the Plone
// implementation, where it is a chrome pagelet slotted between
// plone.pageletlayout.body and the footer rows. Renders nothing without
// children. Each tile carries the child's lede — the one description a page
// has, and the field that maps to Plone's Description.
function subnav(lang, page) {
  if (!page.children?.length) return "";
  return `<nav class="subnav" aria-labelledby="subnav-heading"><div class="shell">
    <h2 class="subnav__heading" id="subnav-heading">${navigation[lang].subnavTitle}</h2>
    <ul class="subnav__list">${page.children.map((key) => `<li><a href="${href(lang, key)}"><span class="subnav__title">${childLabel(lang, key)}</span><span class="subnav__text">${pages[lang][key].lede}</span></a></li>`).join("")}</ul>
  </div></nav>`;
}

function renderOverview(lang, page) {
  return `${pageHero(page)}<section class="section"><div class="shell"><h2 class="section-heading">${page.introTitle}</h2><p class="section-intro">${page.intro}</p>${pillarLine(lang, page.children)}</div></section>`;
}

function renderDetail(lang, page) {
  const labels = lang === "de" ? ["Geeignet für", "Technische Grundlage", "Zeithorizont"] : ["Suitable for", "Technical foundation", "Horizon"];
  const deliverablesTitle = lang === "de" ? "Was wir gemeinsam erarbeiten" : "What we build together";
  const childPages = page.children?.length
    ? `<section class="section section--soft"><div class="shell"><h2 class="section-heading">${page.childrenTitle}</h2>${triage(lang, page.children)}</div></section>`
    : "";
  return `${pageHero(page)}<section class="section"><div class="shell detail-grid"><div class="prose"><h2>${page.bodyTitle}</h2>${page.body.map((text) => `<p>${text}</p>`).join("")}<h2>${deliverablesTitle}</h2><ul>${page.deliverables.map((item) => `<li>${item}</li>`).join("")}</ul></div><dl class="detail-aside"><dt>${labels[0]}</dt><dd>${page.fit}</dd><dt>${labels[1]}</dt><dd>${page.foundation}</dd><dt>${labels[2]}</dt><dd>${page.horizon}</dd></dl></div></section>${childPages}<section class="section section--band"><div class="shell proof-band"><blockquote>“${page.quote}”<cite>— ${lang === "de" ? "Arbeitsprinzip, derico" : "Working principle, derico"}</cite></blockquote><div class="proof-links">${page.proofLinks.map(([target, label]) => `<a href="${resolvedHref(lang, target)}"${target.startsWith("http") ? ' rel="external"' : ""}>${label}</a>`).join("")}</div></div></section>`;
}

const sustainabilityEssay = {
  de: {
    byline: "Von Maik Derstappen",
    opening: [
      "Bei nachhaltiger Softwareentwicklung denken viele zunächst an Energieverbrauch und effiziente Infrastruktur. Das sind wichtige Themen. Hier geht es jedoch um eine andere Form der Nachhaltigkeit: um den langfristigen Erhalt von Investitionen, Wissen und digitaler Handlungsfähigkeit.",
      "Eine Geschäftsanwendung ist selten nur ein Werkzeug, das einmal gekauft und anschließend unverändert verwendet wird. Mit jedem Jahr fließen weitere Arbeit, Erfahrungen und Daten hinein. Abläufe werden angepasst, Mitarbeitende geschult und Schnittstellen geschaffen. Die Software wird zu einem Teil des Unternehmens.",
    ],
    thesis: "Open Source ist allein noch keine Garantie für nachhaltige Software. Aber Open Source ist die notwendige Voraussetzung dafür, eine bestehende Lösung unabhängig vom ursprünglichen Anbieter erhalten und weiterentwickeln zu können.",
    leadQuestion: { label: "Die Leitfrage", text: "Was geschieht, wenn der heutige Hersteller oder Dienstleister morgen nicht mehr zur Verfügung steht?" },
    caseStudy: {
      label: "Aus der Praxis",
      title: "Wenn die eigenen Daten nicht wirklich erreichbar sind",
      paragraphs: [
        "Ein Kunde von uns hatte über viele Jahre eine proprietäre Anwendung zur Erfassung von Trainingsdaten im Sportbereich eingesetzt. Später sollten diese Daten auch auf seiner Website erscheinen. Die Anwendung bot jedoch weder eine dokumentierte Schnittstelle noch einen zugänglichen Datenbestand. Verfügbar war lediglich eine bereits erzeugte HTML-Ansicht, die wir mit zusätzlichem Aufwand aufbereiten konnten.",
        "Eine saubere und dauerhaft tragfähige Anbindung war auf diesem Weg nicht möglich. Der Hersteller wollte keine Schnittstelle bereitstellen oder entwickeln. Aus seiner Sicht war der Kunde dafür zu klein. Damit entschied nicht der Bedarf des Kunden, sondern die Priorität des Anbieters darüber, was mit den über Jahre erfassten Daten geschehen konnte.",
      ],
      scenario: {
        title: "Übertragen auf ein ERP-System",
        paragraphs: [
          "Sie führen es ein, passen Arbeitsabläufe an, schulen Ihr Team und sammeln über Jahre Kunden-, Produkt- und Prozessdaten. Wenn Sie dieses System nicht unabhängig betreiben, erweitern oder ablösen können, liegt ein Teil Ihrer geschäftlichen Handlungsfähigkeit außerhalb Ihrer Kontrolle.",
          "Bei einem zentralen ERP-System kann eine solche Sackgasse existenzbedrohend werden.",
        ],
      },
    },
    chapters: [
      {
        title: "Auch ein großer Hersteller ist keine dauerhafte Absicherung",
        paragraphs: [
          "Ein bekannter Anbieter, ein langfristiger Vertrag oder hohe Lizenzkosten können Verlässlichkeit vermitteln. Sie beseitigen die grundsätzliche Abhängigkeit jedoch nicht. Unternehmen werden verkauft, Produkte eingestellt und Geschäftsmodelle verändert. Preise können steigen, Schnittstellen verschwinden und wichtige Erweiterungen abgelehnt werden. Selbst ein wirtschaftlich stabiler Hersteller kann entscheiden, dass eine Produktlinie oder eine kleine Kundengruppe nicht mehr zu seiner Strategie passt.",
          "Bei proprietärer Software bleiben zentrale Entscheidungen beim Anbieter. Kunden erwerben Nutzungsrechte und Dienstleistungen, aber nicht automatisch die Möglichkeit, die Anwendung selbst oder durch einen anderen Dienstleister weiterführen zu lassen. Viel gezahltes Geld ändert an dieser Grenze nichts.",
          "Für kleine, preiswerte und leicht ersetzbare Werkzeuge kann dieses Risiko vertretbar sein. Voraussetzung ist, dass alle relevanten Daten jederzeit vollständig und ohne Mitwirkung des Herstellers exportiert werden können. Bei größeren, langfristig genutzten Anwendungen sollte dagegen bereits vor der Einführung eine belastbare Ausstiegsstrategie bestehen.",
        ],
      },
      {
        title: "Open Source erhält die Möglichkeit, weiterzugehen",
        paragraphs: [
          "Open Source bedeutet mehr, als Quellcode ansehen zu können. Eine freie Lizenz muss das Recht einräumen, die Software zu verwenden, zu untersuchen, zu verändern und weiterzugeben. Erst diese Rechte schaffen die Grundlage dafür, Verantwortung zu übernehmen oder an einen anderen Partner zu übertragen.",
          "Fällt ein Dienstleister aus, kann ein anderer auf dem vorhandenen Stand aufbauen. Verschwindet ein Hersteller, bleibt die Software nutzbar. Wird eine dringend benötigte Funktion nicht umgesetzt, kann das eigene Team oder ein beauftragtes Unternehmen sie entwickeln. Der ursprüngliche Anbieter verliert damit die Macht, jede weitere Entwicklung zu verhindern.",
          "Das macht einen Wechsel nicht automatisch einfach oder günstig. Schlecht strukturierter Quellcode, fehlende Dokumentation und veraltete Abhängigkeiten können auch ein offenes Projekt schwer wartbar machen. Der entscheidende Unterschied lautet: Bei Open Source kann ein schwieriger Weg vor Ihnen liegen. Bei einer geschlossenen Lösung kann der Weg rechtlich oder technisch vollständig versperrt sein.",
        ],
        facts: {
          label: "Was Offenheit ändert",
          items: [
            ["Ausfall", "Ein anderer Dienstleister kann übernehmen."],
            ["Fehlende Funktion", "Das eigene Team oder ein beauftragtes Unternehmen kann sie entwickeln."],
            ["Anbieterwechsel", "Er kann aufwendig sein, bleibt aber möglich."],
          ],
        },
      },
      {
        title: "Offenheit ersetzt keine Verantwortung",
        paragraphs: [
          "Open Source bedeutet weder „kostenlos“ noch „ohne Ansprechpartner“. Entwicklung, Betrieb, Wartung und Wissenstransfer müssen weiterhin finanziert und organisiert werden. Verlässliche Ansprechpartner entstehen durch ein verantwortliches internes Team oder klare Verträge mit einem oder mehreren Dienstleistern — nicht allein durch das Logo eines Herstellers.",
          "Auch Sicherheit folgt nicht automatisch aus einem offenen oder geschlossenen Entwicklungsmodell. Entscheidend sind überprüfbare Prozesse, zeitnahe Aktualisierungen, gepflegte Abhängigkeiten und ein klarer Umgang mit Sicherheitsmeldungen. Offener Quellcode ermöglicht zusätzliche Prüfungen und unabhängige Korrekturen. Nutzen entsteht daraus aber nur, wenn jemand diese Möglichkeiten tatsächlich wahrnimmt.",
        ],
      },
    ],
    sharing: {
      title: "Geteilte Entwicklung vervielfacht den Nutzen",
      paragraphs: [
        "Ein weiterer Vorteil entsteht, wenn offen entwickelte Bausteine von mehreren Organisationen genutzt werden. Dafür braucht es nicht immer ein gemeinsam geplantes Großprojekt. Zusammenarbeit geschieht in Open-Source-Projekten häufig zeitversetzt.",
        "Eine Organisation finanziert eine Funktion, weil sie diese heute benötigt, und veröffentlicht den entstandenen Baustein. Andere setzen ihn später ein, beheben Fehler, ergänzen Schnittstellen oder übernehmen Teile der Pflege. Jahre später kann auch der ursprüngliche Auftraggeber eine verbesserte und aktualisierte Version nutzen, ohne sämtliche dazwischenliegenden Arbeiten selbst finanziert zu haben.",
        "Dabei bezahlt ein Unternehmen nicht dafür, dem Wettbewerb etwas zu schenken. Es bezahlt zunächst dafür, sein eigenes Problem zum benötigten Zeitpunkt zu lösen. Gleichzeitig kann es auf einer Grundlage aufbauen, in die andere bereits investiert haben, und künftig von deren Beiträgen profitieren.",
      ],
      principles: [
        ["Gemeinsam nutzbar", "Allgemeine Funktionen, Standards und technische Grundlagen können offen weiterentwickelt werden."],
        ["Individuell geschützt", "Spezifische Geschäftslogik oder wettbewerbsrelevante Abläufe müssen nicht öffentlich werden."],
        ["Vom Kunden entschieden", "Unsere Kunden erhalten immer den vollständigen Quellcode und entscheiden selbst, welche Bestandteile sie mit der Gemeinschaft teilen."],
      ],
    },
    publicMoney: {
      title: "Öffentlich finanziert sollte öffentlich nutzbar werden",
      paragraphs: [
        "Besonders groß ist das Potenzial bei öffentlich finanzierten Individualentwicklungen. Behörden, Kommunen, Bildungseinrichtungen und andere öffentliche Organisationen benötigen häufig ähnliche Funktionen. Werden einzelne Bausteine offen entwickelt, kann aus mehreren zunächst lokalen Vorhaben schrittweise eine gemeinsame Lösung entstehen.",
        "Das spart nicht automatisch jede doppelte Ausgabe. Anwendungen müssen weiterhin angepasst, geprüft, betrieben und gepflegt werden. Aber öffentliche Mittel schaffen auf diese Weise einen bleibenden Wert, den andere Stellen nutzen und weiterentwickeln können. Deshalb sollten öffentlich finanzierte Individualentwicklungen grundsätzlich unter einer freien Lizenz veröffentlicht werden.",
      ],
      statement: "Öffentliches Geld sollte öffentlichen Code schaffen.",
    },
    checklist: {
      title: "Eine freie Lizenz allein reicht nicht",
      intro: "Nachhaltigkeit entsteht durch Rechte, technische Qualität, Pflege und geteiltes Wissen. Diese Grundlagen halten eine Anwendung langfristig übertragbar.",
      items: [
        "Eine anerkannte freie Lizenz und vollständiger Quellcode",
        "Offene Datenformate, dokumentierte Schnittstellen und ein vollständiger Datenexport",
        "Verständliche Architektur und nachvollziehbare technische Entscheidungen",
        "Automatisierte Tests sowie aktuelle Dokumentation",
        "Reproduzierbare Installation und Bereitstellung",
        "Regelmäßige Sicherheitsaktualisierungen und geplante Versionswechsel",
        "Offene Standards und möglichst verbreitete Technologien",
        "Zugriff des Kunden auf Quellcode und betriebliche Infrastruktur",
        "Wissenstransfer an das eigene Team, soweit es dies leisten kann und möchte",
      ],
    },
    responsibility: {
      title: "Verantwortung zeigt sich auch in schwierigen Projekten",
      paragraphs: [
        "Bei derico entwickeln wir Anwendungen so, dass sie nicht dauerhaft von uns abhängig bleiben müssen. Kunden erhalten den vollständigen Quellcode. Dokumentation, Tests, offene Standards und nachvollziehbare Betriebswege sollen es eigenen Mitarbeitenden oder anderen Dienstleistern ermöglichen, Verantwortung zu übernehmen. Wo es sinnvoll ist, fließen allgemeine Verbesserungen in die zugrunde liegenden Open-Source-Projekte zurück.",
        "Zu dieser Haltung gehört auch die Ausdauer, schwierige Projekte zu stabilisieren. Wir haben Anwendungen übernommen, bei denen Wartungsrückstände, fehlendes Wissen oder technische Altlasten den nächsten Schritt erschwerten.",
        "Nachhaltig zu arbeiten heißt für uns dann nicht, vorschnell alles neu zu bauen. Es heißt, den vorhandenen Wert zu verstehen, Risiken zu ordnen und die Lösung Schritt für Schritt wieder in einen langfristig tragfähigen Zustand zu bringen.",
      ],
      aside: { label: "Unser Arbeitsprinzip", text: "Ausdauer gehört zur Nachhaltigkeit. Auch unbequeme Aufräumarbeiten können der richtige Weg zu einer langfristig besseren Lösung sein." },
    },
    exit: {
      label: "Ihre Ausstiegsstrategie",
      title: "Bleiben Sie handlungsfähig?",
      intro: "Eine nachhaltige Anwendung muss nicht unabhängig von allen Menschen und Unternehmen sein. Aber sie darf nicht in einer Sackgasse enden, sobald sich ein Partner, ein Produkt oder ein Geschäftsmodell verändert.",
      questions: [
        "Haben Sie Zugriff auf den vollständigen Quellcode, Ihre Daten und die notwendige Dokumentation?",
        "Dürfen Sie einen anderen Dienstleister mit Betrieb und Weiterentwicklung beauftragen?",
        "Können Sie Ihre Daten vollständig und in einem dokumentierten Format exportieren?",
        "Ist nachvollziehbar, wie die Anwendung installiert, getestet und aktualisiert wird?",
        "Was geschieht, wenn der heutige Hersteller oder Dienstleister morgen nicht mehr verfügbar ist?",
      ],
      conclusion: "Open Source erhält die Freiheit, den nächsten Schritt selbst zu bestimmen — und schützt damit den Wert, der über viele Jahre in einer Anwendung entsteht.",
    },
    sources: {
      title: "Weiterführende Hinweise",
      links: [
        ["https://opensource.org/osd", "Open Source Initiative: Definition von Open Source"],
        ["https://publiccode.eu/de/", "Free Software Foundation Europe: Öffentliches Geld? Öffentlicher Code!"],
        ["https://digital-strategy.ec.europa.eu/en/library/study-about-impact-open-source-software-and-hardware-technological-independence-competitiveness-and", "Europäische Kommission: Studie zu den wirtschaftlichen Auswirkungen von Open-Source-Software und -Hardware"],
      ],
    },
  },
  en: {
    byline: "By Maik Derstappen",
    opening: [
      "When people hear “sustainable software development”, many first think of energy consumption and efficient infrastructure. Those are important topics. This essay is about a different kind of sustainability: preserving investments, knowledge and the ability to act digitally over the long term.",
      "A business application is rarely just a tool that is bought once and then used unchanged. Every year, more work, experience and data flow into it. Processes are adapted, staff are trained and interfaces are built. The software becomes part of the company.",
    ],
    thesis: "Open source alone is no guarantee of sustainable software. But open source is the necessary precondition for keeping an existing solution alive and developing it further, independently of the original vendor.",
    leadQuestion: { label: "The guiding question", text: "What happens if today’s vendor or service provider is no longer available tomorrow?" },
    caseStudy: {
      label: "From practice",
      title: "When your own data is not really within reach",
      paragraphs: [
        "One of our clients had used a proprietary application for recording training data in sports for many years. Later, that data was also meant to appear on their website. The application, however, offered neither a documented interface nor an accessible data store. All that was available was a pre-rendered HTML view, which we could process only with additional effort.",
        "A clean, permanently viable integration was not possible on that route. The vendor did not want to provide or develop an interface. From their point of view, the client was too small for that. So it was not the client’s need but the vendor’s priorities that decided what could happen to data collected over many years.",
      ],
      scenario: {
        title: "Applied to an ERP system",
        paragraphs: [
          "You introduce it, adapt your workflows, train your team and collect customer, product and process data over years. If you cannot operate, extend or replace that system independently, part of your business’s ability to act lies outside your control.",
          "With a central ERP system, a dead end like this can threaten the company’s existence.",
        ],
      },
    },
    chapters: [
      {
        title: "Even a large vendor is no lasting safeguard",
        paragraphs: [
          "A well-known vendor, a long-term contract or high licence fees can convey reliability. They do not remove the underlying dependency. Companies are sold, products are discontinued and business models change. Prices can rise, interfaces can disappear and important extensions can be refused. Even a financially stable vendor can decide that a product line or a small group of customers no longer fits its strategy.",
          "With proprietary software, the central decisions stay with the vendor. Customers acquire usage rights and services, but not automatically the ability to continue the application themselves or through another service provider. Paying a lot of money does nothing to change that boundary.",
          "For small, inexpensive and easily replaceable tools, this risk can be acceptable. The precondition is that all relevant data can be exported completely, at any time and without the vendor’s involvement. For larger applications used over the long term, a robust exit strategy should exist before they are introduced.",
        ],
      },
      {
        title: "Open source keeps the road open",
        paragraphs: [
          "Open source means more than being able to look at source code. A free licence must grant the right to use, study, modify and redistribute the software. Only these rights create the basis for taking responsibility, or for handing it to another partner.",
          "If a service provider drops out, another can build on the existing state. If a vendor disappears, the software remains usable. If an urgently needed feature is not implemented, your own team or a contracted company can develop it. The original vendor loses the power to block every further development.",
          "That does not automatically make a change easy or cheap. Poorly structured source code, missing documentation and outdated dependencies can make an open project hard to maintain as well. The decisive difference is this: with open source, a difficult road may lie ahead of you. With a closed solution, the road may be completely blocked, legally or technically.",
        ],
        facts: {
          label: "What openness changes",
          items: [
            ["Provider drops out", "Another service provider can take over."],
            ["Missing feature", "Your own team or a contracted company can develop it."],
            ["Change of vendor", "It may be laborious, but it remains possible."],
          ],
        },
      },
      {
        title: "Openness does not replace responsibility",
        paragraphs: [
          "Open source means neither “free of charge” nor “nobody to call”. Development, operations, maintenance and knowledge transfer still have to be funded and organised. Reliable contacts come from a responsible in-house team or clear contracts with one or more service providers — not from a vendor’s logo alone.",
          "Security does not follow automatically from an open or a closed development model either. What matters are verifiable processes, timely updates, well-maintained dependencies and a clear way of handling security reports. Open source code allows additional reviews and independent fixes. But that only creates value if someone actually takes up those opportunities.",
        ],
      },
    ],
    sharing: {
      title: "Shared development multiplies the benefit",
      paragraphs: [
        "A further advantage arises when openly developed building blocks are used by several organisations. That does not always require a jointly planned large project. In open-source projects, collaboration often happens at different points in time.",
        "One organisation funds a feature because it needs it today, and publishes the resulting building block. Others adopt it later, fix bugs, add interfaces or take over part of the maintenance. Years later, the original client can use an improved and updated version without having funded all the work in between.",
        "In doing so, a company is not paying to give something away to its competitors. It pays, first of all, to solve its own problem at the moment it needs solving. At the same time it can build on a foundation others have already invested in, and benefit from their contributions in future.",
      ],
      principles: [
        ["Shared in common", "General features, standards and technical foundations can be developed further in the open."],
        ["Individually protected", "Specific business logic or competitively relevant processes do not have to become public."],
        ["Decided by the client", "Our clients always receive the complete source code and decide for themselves which parts they share with the community."],
      ],
    },
    publicMoney: {
      title: "Publicly funded should become publicly usable",
      paragraphs: [
        "The potential is particularly large for publicly funded custom development. Public authorities, municipalities, educational institutions and other public organisations often need similar features. If individual building blocks are developed in the open, several initially local projects can gradually grow into a shared solution.",
        "That does not automatically save every duplicate expense. Applications still have to be adapted, tested, operated and maintained. But this way, public funds create a lasting value that other bodies can use and develop further. Publicly funded custom development should therefore be released under a free licence as a matter of principle.",
      ],
      statement: "Public money should create public code.",
    },
    checklist: {
      title: "A free licence alone is not enough",
      intro: "Sustainability comes from rights, technical quality, care and shared knowledge. These foundations keep an application transferable in the long run.",
      items: [
        "A recognised free licence and the complete source code",
        "Open data formats, documented interfaces and a complete data export",
        "An understandable architecture and traceable technical decisions",
        "Automated tests and up-to-date documentation",
        "Reproducible installation and deployment",
        "Regular security updates and planned version upgrades",
        "Open standards and technologies that are as widely used as possible",
        "Client access to the source code and the operational infrastructure",
        "Knowledge transfer to the client’s own team, as far as it can and wants to take it on",
      ],
    },
    responsibility: {
      title: "Responsibility shows in difficult projects too",
      paragraphs: [
        "At derico we build applications so that they do not have to stay dependent on us permanently. Clients receive the complete source code. Documentation, tests, open standards and traceable operating procedures are meant to let their own staff or other service providers take responsibility. Where it makes sense, general improvements flow back into the underlying open-source projects.",
        "Part of this attitude is the stamina to stabilise difficult projects. We have taken over applications where maintenance backlogs, missing knowledge or technical legacy made the next step hard.",
        "For us, working sustainably then does not mean hastily rebuilding everything. It means understanding the value that is there, ordering the risks and bringing the solution back, step by step, into a state that will carry it for the long term.",
      ],
      aside: { label: "How we work", text: "Stamina is part of sustainability. Even uncomfortable clean-up work can be the right road to a solution that is better in the long run." },
    },
    exit: {
      label: "Your exit strategy",
      title: "Do you keep your room to act?",
      intro: "A sustainable application does not have to be independent of every person and every company. But it must not end in a dead end as soon as a partner, a product or a business model changes.",
      questions: [
        "Do you have access to the complete source code, your data and the necessary documentation?",
        "Are you allowed to commission another service provider for operations and further development?",
        "Can you export your data completely and in a documented format?",
        "Is it traceable how the application is installed, tested and updated?",
        "What happens if today’s vendor or service provider is no longer available tomorrow?",
      ],
      conclusion: "Open source preserves the freedom to decide the next step yourself — and with it, the value that builds up in an application over many years.",
    },
    sources: {
      title: "Further reading",
      links: [
        ["https://opensource.org/osd", "Open Source Initiative: The Open Source Definition"],
        ["https://publiccode.eu/en/", "Free Software Foundation Europe: Public Money? Public Code!"],
        ["https://digital-strategy.ec.europa.eu/en/library/study-about-impact-open-source-software-and-hardware-technological-independence-competitiveness-and", "European Commission: Study about the impact of open source software and hardware on technological independence, competitiveness and innovation"],
      ],
    },
  },
};

const paragraphs = (items) => items.map((text) => `<p>${text}</p>`).join("");

function renderSustainability(lang, page) {
  const essay = sustainabilityEssay[lang];
  const { caseStudy, sharing, publicMoney, checklist, responsibility, exit, sources } = essay;
  const chapters = essay.chapters.map((chapter) => {
    const facts = chapter.facts
      ? `<aside class="article-aside"><p class="page-context">${chapter.facts.label}</p><dl class="article-facts">${chapter.facts.items.map(([term, text]) => `<div><dt>${term}</dt><dd>${text}</dd></div>`).join("")}</dl></aside>`
      : "";
    return `<div class="article-prose"><h2>${chapter.title}</h2>${paragraphs(chapter.paragraphs)}</div>${facts}`;
  }).join("");
  return `<article class="sustainability-article">${pageHero(page)}
      <section class="section article-opening"><div class="shell article-layout">
        <div class="article-prose article-prose--opening"><p class="article-byline">${essay.byline}</p>${paragraphs(essay.opening)}<blockquote class="article-thesis">${essay.thesis}</blockquote></div>
        <aside class="article-aside"><p class="page-context">${essay.leadQuestion.label}</p><p>${essay.leadQuestion.text}</p></aside>
      </div></section>

      <section class="section section--soft case-study"><div class="shell">
        <header class="case-study__header"><p class="page-context">${caseStudy.label}</p><h2>${caseStudy.title}</h2></header>
        <div class="case-study__grid"><div class="article-prose">${paragraphs(caseStudy.paragraphs)}</div><aside class="article-scenario"><h3>${caseStudy.scenario.title}</h3>${paragraphs(caseStudy.scenario.paragraphs)}</aside></div>
      </div></section>

      <section class="section"><div class="shell article-layout">${chapters}</div></section>

      <section class="section section--band"><div class="shell sharing-grid">
        <h2 class="section-heading">${sharing.title}</h2>
        <div class="article-prose">${paragraphs(sharing.paragraphs)}</div>
        <div class="sharing-principles">${sharing.principles.map(([title, text]) => `<section><h3>${title}</h3><p>${text}</p></section>`).join("")}</div>
      </div></section>

      <section class="section"><div class="shell article-layout">
        <div class="article-prose"><h2>${publicMoney.title}</h2>${paragraphs(publicMoney.paragraphs)}</div>
        <blockquote class="public-code-statement"><p>${publicMoney.statement}</p></blockquote>
      </div></section>

      <section class="section section--soft"><div class="shell checklist-layout">
        <header><h2 class="section-heading">${checklist.title}</h2><p class="section-intro">${checklist.intro}</p></header>
        <ul class="sustainability-checklist">${checklist.items.map((item) => `<li>${item}</li>`).join("")}</ul>
      </div></section>

      <section class="section"><div class="shell article-layout">
        <div class="article-prose"><h2>${responsibility.title}</h2>${paragraphs(responsibility.paragraphs)}</div>
        <aside class="article-aside"><p class="page-context">${responsibility.aside.label}</p><p>${responsibility.aside.text}</p></aside>
      </div></section>

      <section class="section exit-section"><div class="shell exit-layout"><header><p class="page-context">${exit.label}</p><h2 class="section-heading">${exit.title}</h2><p>${exit.intro}</p></header><ol class="exit-questions">${exit.questions.map((question) => `<li>${question}</li>`).join("")}</ol><p class="exit-conclusion">${exit.conclusion}</p></div></section>

      <footer class="section article-sources"><div class="shell"><h2>${sources.title}</h2><ul>${sources.links.map(([url, text]) => `<li><a href="${url}" rel="external">${text}</a></li>`).join("")}</ul></div></footer>
    </article>`;
}

function renderTraining(lang, page) {
  const formats = lang === "de" ? [
    ["Team-Workshop", "Ein bis zwei Tage", "Gemeinsames Verständnis für Architektur, Arbeitsweise oder eine anstehende Entscheidung."],
    ["Technische Schulung", "Ein bis drei Tage", "Plone, Odoo, Python oder Svelte mit Übungen an realistischen Beispielen."],
    ["Begleitendes Mentoring", "Über mehrere Wochen", "Regelmäßige Sessions zu Fragen, Reviews und der Anwendung des Gelernten im Projekt."],
  ] : [
    ["Team workshop", "One to two days", "Shared understanding of architecture, working practices or an upcoming decision."],
    ["Technical training", "One to three days", "Plone, Odoo, Python or Svelte with exercises based on realistic examples."],
    ["Ongoing mentoring", "Across several weeks", "Regular sessions for questions, reviews and applying learning within the project."],
  ];
  return `${pageHero(page)}<section class="section"><div class="shell"><h2 class="section-heading">${lang === "de" ? "Formate nach Aufgabe und Team" : "Formats fitted to task and team"}</h2><ul class="talk-list">${formats.map(([title, meta, text]) => `<li><p class="talk-meta">${meta}</p><h3>${title}</h3><p>${text}</p></li>`).join("")}</ul></div></section><section class="section section--soft"><div class="shell proof-band"><div><h2 class="section-heading">${lang === "de" ? "Vorbereitung mit echtem Kontext" : "Preparation with real context"}</h2><p class="section-intro">${lang === "de" ? "Vorab klären wir Ziele, Vorkenntnisse und die eingesetzte Anwendung. Materialien und Übungen werden anschließend für Ihr Team zusammengestellt." : "Beforehand we clarify goals, existing knowledge and the application in use. Materials and exercises are then assembled for your team."}</p></div><div class="proof-links"><a href="${href(lang, "contact")}">${lang === "de" ? "Schulung anfragen" : "Request training"}</a><a href="${href(lang, "talks")}">${lang === "de" ? "Vortragsthemen ansehen" : "View talk topics"}</a></div></div></section>`;
}

function renderTalks(lang, page) {
  const talks = lang === "de" ? [
    ["Konferenzbeitrag", "Anwendungen, die bleiben", "Welche Architekturentscheidungen Wartbarkeit, Upgradefähigkeit und offene Übergaben über viele Jahre ermöglichen."],
    ["Plone & Python", "Werkzeuge, die eine Community weiterträgt", "Erfahrungen aus plonecli, bobtemplates.plone und der Zusammenarbeit in offenen Projekten."],
    ["Team & Technik", "Vom Prototyp zur gepflegten Anwendung", "Wie Domänenmodell, Tests, Betrieb und Verantwortung gemeinsam mit dem Produkt wachsen."],
  ] : [
    ["Conference session", "Applications, grown to last", "Architectural decisions that support maintenance, upgrades and open handovers across many years."],
    ["Plone & Python", "Tools carried forward by a community", "Experience from plonecli, bobtemplates.plone and collaboration in open projects."],
    ["Team & technology", "From prototype to maintained application", "How domain model, tests, operations and responsibility grow with the product."],
  ];
  return `${pageHero(page)}<section class="section"><div class="shell"><h2 class="section-heading">${lang === "de" ? "Aktuelle Themen" : "Current topics"}</h2><ul class="talk-list">${talks.map(([meta, title, text]) => `<li><p class="talk-meta">${meta}</p><h3>${title}</h3><p>${text}</p></li>`).join("")}</ul></div></section><section class="section section--soft"><div class="shell empty-state"><h3>${lang === "de" ? "Neue Termine werden nach Bestätigung veröffentlicht." : "New dates are published once confirmed."}</h3><p>${lang === "de" ? "Für eine Veranstaltung oder ein internes Format können Sie ein Thema direkt anfragen." : "You can request a topic directly for an event or an internal session."}</p><div class="action-row"><a class="button" href="${href(lang, "contact")}">${lang === "de" ? "Vortrag anfragen" : "Request a talk"}</a></div></div></section>`;
}

function renderContact(lang, page) {
  const isDe = lang === "de";
  return `${pageHero(page)}<section class="section"><div class="shell contact-layout"><div class="contact-direct"><h2 class="section-heading">${isDe ? "Direkt erreichbar" : "Reach us directly"}</h2><p class="section-intro">${isDe ? "Maik Derstappen antwortet persönlich. In der Regel erhalten Sie innerhalb von zwei Werktagen eine Rückmeldung." : "Maik Derstappen replies personally. You will usually hear back within two working days."}</p><a href="mailto:md@derico.de">md@derico.de</a><dl class="contact-details"><div><dt>${isDe ? "Telefon" : "Phone"}</dt><dd><a href="tel:+491788612833">+49 178 861 2 833</a></dd></div><div><dt>${isDe ? "Standort" : "Location"}</dt><dd>Laaver Weg 2<br>19273 Neuhaus/Elbe<br>${isDe ? "Deutschland" : "Germany"}</dd></div><div><dt>${isDe ? "Gespräch" : "Conversation"}</dt><dd>${isDe ? "Deutsch oder Englisch · remote oder vor Ort" : "German or English · remote or on site"}</dd></div></dl></div><form class="contact-form" data-contact-form novalidate><h2>${isDe ? "E-Mail vorbereiten" : "Prepare an email"}</h2><p class="muted">${isDe ? "Das Formular öffnet Ihr E-Mail-Programm. Ihre Angaben werden nicht an diese Vorschau übertragen." : "The form opens your email application. Your details are not transmitted to this preview."}</p>${formField(lang, "name", isDe ? "Ihr Name" : "Your name", "text", true)}${formField(lang, "company", isDe ? "Unternehmen" : "Company", "text", false)}${formField(lang, "email", isDe ? "Ihre E-Mail-Adresse" : "Your email address", "email", true)}<div class="form-field"><label for="topic">${isDe ? "Thema" : "Topic"}</label><select id="topic" name="topic"><option>${isDe ? "Neue Anwendung" : "New application"}</option><option>Odoo</option><option>Plone</option><option>Django, Pyramid & FastAPI</option><option>${isDe ? "Support & Wartung" : "Support & maintenance"}</option><option>${isDe ? "Schulung oder Vortrag" : "Training or talk"}</option></select></div><div class="form-field"><label for="message">${isDe ? "Worum geht es?" : "What would you like to discuss?"}</label><textarea id="message" name="message" data-required aria-describedby="message-error" placeholder="${isDe ? "Aufgabe, heutiger Stand und gewünschter nächster Schritt" : "Task, current situation and desired next step"}"></textarea><p class="field-error" id="message-error" hidden></p></div><button class="button" type="submit">${isDe ? "E-Mail im eigenen Programm öffnen" : "Open email in your application"}</button><p class="form-note">${isDe ? "Pflichtfelder: Name, E-Mail-Adresse und Nachricht." : "Required: name, email address and message."}</p><p class="form-status" data-form-status role="status" tabindex="-1" hidden></p></form></div></section>`;
}

function formField(lang, id, label, type, required) {
  return `<div class="form-field"><label for="${id}">${label}</label><input id="${id}" name="${id}" type="${type}"${required ? ` data-required aria-describedby="${id}-error"` : ""}>${required ? `<p class="field-error" id="${id}-error" hidden></p>` : ""}</div>`;
}

function renderImprint(lang, page) {
  const isDe = lang === "de";
  return `${pageHero(page)}<section class="section"><div class="shell"><div class="prose"><h2>${isDe ? "Anbieter" : "Provider"}</h2><p>Maik Derstappen<br>Laaver Weg 2<br>19273 Neuhaus/Elbe<br>${isDe ? "Deutschland" : "Germany"}</p><h2>${isDe ? "Kontakt" : "Contact"}</h2><p>${isDe ? "Telefon" : "Phone"}: <a href="tel:+491788612833">+49 178 861 2 833</a><br>${isDe ? "E-Mail" : "Email"}: <a href="mailto:md@derico.de">md@derico.de</a></p><h2>${isDe ? "Bildnachweis" : "Image credit"}</h2><p>${isDe ? "Das Hintergrundfoto der Startseite stammt von" : "The homepage background photograph is by"} <a href="https://unsplash.com/photos/brown-and-green-trees-on-brown-grass-field-during-daytime-hZX4tYgljUI" rel="external">Kat Closon</a>${isDe ? " und wird unter der" : " and is used under the"} <a href="https://unsplash.com/license" rel="external">Unsplash License</a>${isDe ? " verwendet." : "."}</p></div></div></section>`;
}

const styleguideCopy = {
  de: {
    toc: "Auf dieser Seite",
    spec: { aurora: "In Aurora", font: "Schrift", color: "Farbe", use: "Einsatz" },
    how: {
      title: "So formatieren Sie in Aurora",
      intro: "Das Design kennt für jede Textrolle einen Namen. Sie wählen die Rolle, das Theme übernimmt Schrift, Größe und Farbe. Vier Handgriffe reichen.",
      steps: [
        ["Block einfügen", "In einer leeren Zeile <kbd>/</kbd> tippen. Das Menü „Text blocks“ bietet Text, Heading 2 bis 4, Listen, Toggle, Code Block, Table, Blockquote und Callout."],
        ["Blocktyp wechseln", "Text markieren, in der schwebenden Werkzeugleiste „Turn into“ öffnen: Text, Heading 2/3/4, Bulleted list, Numbered list, To-do list oder Quote."],
        ["Textstil wählen", "Ein Wort markieren. Rechts in der Werkzeugleiste erscheint „Text style“ – bei Listen „List style“, bei Zitaten „Quote style“. Blöcke auf oberster Ebene zeigen dieselbe Auswahl in der Seitenleiste; in Spalten geht es nur über die Werkzeugleiste."],
        ["Breite und Hintergrund", "Block anklicken, in der Seitenleiste „Block width“ und „Background“ setzen. Ein Hintergrund läuft über aufeinanderfolgende Blöcke weiter, bis ein Block ohne folgt."],
      ],
      rulesTitle: "Grundsätze",
      rules: [
        "Eine Seite hat einen Titel – den Titelblock oben. Überschriften beginnen bei Heading 2.",
        "Überschriften gliedern, sie machen nichts groß. Wer eine große oder farbige Zeile braucht, nimmt einen Textstil.",
        "„Normal“ entfernt einen Stil wieder. Ein Block ohne Stil sieht aus wie immer.",
        "Farben werden nie direkt gewählt. Sie kommen aus Stil, Hintergrund und Theme – so bleibt jede Kombination lesbar.",
        "Nichts unter 15 Pixel. Es gibt kein Kleingedrucktes; Hierarchie entsteht aus Gewicht, Farbe und Abstand.",
      ],
    },
    fonts: {
      title: "Schriften",
      intro: "Zwei Schriften tragen die Seite. Beide liegen auf dem Server, nichts wird von Dritten geladen.",
      items: [
        ["Source Sans 3", "Fließtext, Listen, Navigation, Byline, Term", "Die Arbeitsschrift. 16 Pixel Grundgröße, Zeilenabstand 1,6."],
        ["Literata", "Überschriften, Kicker, Statement, Zitate", "Die Display-Schrift, ein Lesefont aus dem Buchdruck. Erscheint überall dort, wo eine Zeile für sich stehen soll."],
      ],
      sample: "Anwendungen, die bleiben. Nachhaltige Lösungen seit über zwanzig Jahren – flexibel, modern, sicher.",
    },
    headings: {
      title: "Überschriften",
      intro: "Vier Stufen, alle in Literata. Die Stufe folgt der Gliederung, nicht der gewünschten Größe.",
      entries: [
        { level: "title", sample: "Odoo verbindet Ihre Geschäftsprozesse.", aurora: "Titelblock (einmal pro Seite)", font: "Literata 600 · 32–56 px", color: "Ink", use: "Der Seitentitel. Wird aus dem Titel der Seite gefüllt, nicht getippt." },
        { level: "h2", sample: "Was wir gemeinsam erarbeiten", aurora: "Heading 2", font: "Literata 600 · 26–39 px", color: "Ink", use: "Kapitel. Die erste Stufe, die Sie selbst setzen." },
        { level: "h3", sample: "Zuständigkeiten und Reaktionswege", aurora: "Heading 3", font: "Literata 600 · 22–28 px", color: "Ink", use: "Abschnitt innerhalb eines Kapitels." },
        { level: "h4", sample: "Upgrade-Zyklen", aurora: "Heading 4", font: "Source Sans 3 700 · 18 px", color: "Ink", use: "Zwischenzeile in langen Abschnitten. Sparsam." },
      ],
    },
    text: {
      title: "Textstile",
      intro: "Das Menü „Text style“ auf einem Absatz. Sieben Rollen, benannt nach ihrer Aufgabe im Text.",
      entries: [
        { style: "normal", sample: "<p>Wir entwickeln Geschäftsanwendungen auf Basis von Python, modernem JavaScript und Open Source. Wartbarkeit, offene Standards und klare Entscheidungen sichern ihren Wert über viele Jahre.</p>", aurora: "Text style → Normal", font: "Source Sans 3 · 16 px · Zeilenabstand 1,6", color: "Ink", use: "Fließtext. Die Lesebreite liegt bei 66 Zeichen." },
        { style: "kicker", sample: "<p class=\"sg-kicker\">Aus der Praxis</p><h2 class=\"sg-h2\">Ein Verband, drei Systeme, ein Datenmodell</h2>", aurora: "Text style → Kicker", font: "Literata kursiv · 16 px", color: "Accent (Copper text)", use: "Die Zeile über einer Überschrift oder einem Statement. Bindet sich an das, was folgt: kein Abstand darunter." },
        { style: "lede", sample: "<p class=\"sg-lede\">Technologie ist tragfähig, wenn sie zur Aufgabe passt, verständlich bleibt und zuverlässig weiterentwickelt werden kann.</p>", aurora: "Text style → Lede", font: "Source Sans 3 · 18–22 px · Zeilenabstand 1,5", color: "Soft (Ink soft)", use: "Der Vorspann unter einer Überschrift. Ein Absatz, selten zwei." },
        { style: "statement", sample: "<p class=\"sg-statement\">Nachhaltig ist eine Anwendung, die nach zehn Jahren noch jemand versteht.</p>", aurora: "Text style → Statement", font: "Literata · 18–22 px · Zeilenabstand 1,5", color: "Ink", use: "Eine Aussage, die für sich steht – in einer Randspalte oder als Schluss eines Kapitels. Bis 30 Zeichen Breite." },
        { style: "byline", sample: "<p class=\"sg-byline\">Von Maik Derstappen</p>", aurora: "Text style → Byline", font: "Source Sans 3 700 · 16 px", color: "Accent (Copper text)", use: "Die Autorenzeile über dem ersten Absatz eines Beitrags." },
        { style: "term", sample: "<p class=\"sg-term\">Laufzeit</p><p class=\"sg-muted\">Seit 2009 in Betrieb, dreimal migriert, nie neu geschrieben.</p>", aurora: "Text style → Term", font: "Source Sans 3 700 · 16 px", color: "Strong (Brand deep)", use: "Der Begriff einer Faktenliste. Bindet sich an den Absatz darunter, der meist „Muted“ ist." },
        { style: "muted", sample: "<p class=\"sg-muted\">Kontaktdaten und Telefonnummern sind Platzhalter der aktuellen Seite und werden vor der Veröffentlichung geprüft.</p>", aurora: "Text style → Muted", font: "Source Sans 3 · 16 px", color: "Soft (Ink soft)", use: "Zurückgenommener Text: Erläuterungen, Definitionen, Nebensätze." },
      ],
    },
    lists: {
      title: "Listenstile",
      intro: "Das Menü „List style“ auf einem Listeneintrag. Der Stil gilt für die ganze Liste, nicht für einen Eintrag.",
      entries: [
        { style: "normal", sample: "<ul><li>Architektur, Benutzeroberfläche und Betrieb als eine Aufgabe</li><li>Frameworks nach Prozess und Lebensdauer gewählt</li><li>Offene Standards statt Abhängigkeiten</li></ul>", aurora: "List style → Normal (Bulleted list, Numbered list, To-do list)", font: "Source Sans 3 · 16 px", color: "Ink", use: "Die gewöhnliche Aufzählung. Nummeriert, wenn die Reihenfolge zählt." },
        { style: "checklist", sample: "<ul class=\"sg-list sg-list--checklist\"><li>Der Quellcode gehört Ihnen und liegt in Ihrem Repository.</li><li>Jede Abhängigkeit ist offen lizenziert und aktiv gepflegt.</li><li>Ein Upgrade-Pfad ist vor dem Start beschrieben.</li></ul>", aurora: "List style → Checklist", font: "Source Sans 3 · 16 px · Haken in Copper", color: "Ink, Haken Accent", use: "Kriterien, die erfüllt sind oder sein sollen. Kein Aufzählungspunkt, ein Haken je Zeile, Haarlinie darüber." },
        { style: "questions", sample: "<ol class=\"sg-list sg-list--questions\"><li>Wer kann die Anwendung in fünf Jahren noch weiterentwickeln?</li><li>Welche Daten müssen exportierbar bleiben – und in welchem Format?</li><li>Was passiert, wenn der Anbieter aufhört?</li></ol>", aurora: "List style → Questions", font: "Source Sans 3 · 16 px · Zähler in Literata 700", color: "Ink, Zähler Accent", use: "Die Fragen zum Mitnehmen am Ende eines Beitrags. Nummeriert, mit Linien über jeder Zeile und unter der letzten." },
        { style: "sources", sample: "<ul class=\"sg-list sg-list--sources\"><li><a href=\"#\">Bundesministerium des Innern: Open-Source-Strategie (2024)</a></li><li><a href=\"#\">Plone Foundation: Release history</a></li></ul>", aurora: "List style → Sources", font: "Source Sans 3 · 16 px", color: "Soft (Ink soft)", use: "Quellen und Verweise. Ruhige Zeilen, Links in weichem Ink." },
      ],
    },
    quotes: {
      title: "Zitatstile",
      intro: "Das Menü „Quote style“ auf einem Blockquote.",
      entries: [
        { style: "normal", sample: "<blockquote class=\"sg-quote\">Wir wählen Frameworks nach Prozess, Organisation und Lebensdauer der Anwendung.</blockquote>", aurora: "Quote style → Normal (Blockquote)", font: "Source Sans 3 kursiv · 16 px", color: "Soft, Linie Band rule", use: "Ein Zitat im Lauf des Textes. Linie links, kursiv." },
        { style: "statement", sample: "<blockquote class=\"sg-quote sg-quote--statement\">Software ist dann nachhaltig, wenn man sie loslassen kann, ohne sie zu verlieren.</blockquote>", aurora: "Quote style → Statement", font: "Literata 500 · 20–28 px · Zeilenabstand 1,4", color: "Strong (Brand deep), Linie Band rule", use: "Die These eines Beitrags. Linie oben, bis 36 Zeichen Breite." },
        { style: "display", sample: "<blockquote class=\"sg-quote sg-quote--display\">Public Money, Public Code.</blockquote>", aurora: "Quote style → Display", font: "Literata 650 · 28–48 px · Zeilenabstand 1,18", color: "Strong (Brand deep), Linie Band rule", use: "Eine Zeile als Plakat. Wenige Worte, bis 22 Zeichen Breite. Einmal pro Seite." },
      ],
    },
    marks: {
      title: "Auszeichnungen",
      intro: "Für Wörter innerhalb eines Absatzes. Text markieren, Schaltfläche in der Werkzeugleiste. Auf Windows und Linux steht Strg für ⌘.",
      entries: [
        ["Bold", "<strong>Verlässliche Betreuung</strong> für Anwendungen, die täglich gebraucht werden.", "⌘ B", "Ein Begriff, der beim Überfliegen hängen bleiben soll. Nie ganze Sätze."],
        ["Italic", "Das Wort <em>nachhaltig</em> meint hier Wartbarkeit, nicht Marketing.", "⌘ I", "Betonung, Fremdwörter, Titel von Werken."],
        ["Strikethrough", "Reaktion <s>innerhalb von zwei Werktagen</s> am selben Werktag.", "⌘ ⇧ M", "Eine Korrektur, die sichtbar bleiben soll. Selten."],
        ["Code", "Der Befehl <code>uv run pytest</code> führt die Tests aus.", "⌘ E", "Befehle, Dateinamen, Bezeichner."],
        ["Link", "Mehr dazu auf <a href=\"#\">plone.org</a>.", "Link-Schaltfläche", "Verweise. Der Linktext sagt, wohin es geht – nie „hier“."],
      ],
    },
    colors: {
      title: "Farben",
      intro: "Die Palette „Jahresringe“: Petrol als Marke, Kupfer als Akzent. Redaktionell wählen Sie nie eine Farbe – jeder Textstil und jeder Hintergrund bringt seine mit. Die Namen in Klammern sind die Token, die Aurora und das Theme benutzen.",
      groups: [
        { title: "Grund und Text", note: "Was jede Seite trägt.", swatches: [
          ["Ground", "ground", "#fafcfd", "Der Seitengrund."],
          ["Surface", "surface", "#ebf6f8", "Ruhige Fläche. Hintergrund „Grey“."],
          ["Ink", "ink", "#101d22", "Fließtext, Überschriften."],
          ["Ink soft", "ink-soft", "#31464e", "Aurora „Soft“: Lede, Muted, Sources."],
          ["Rule", "rule", "#b9cfd5", "Haarlinien: Checklist, Questions."],
          ["Band rule", "band-rule", "#53838f", "Strukturlinien: Zitate, Bänder."],
        ] },
        { title: "Petrol", note: "Die Marke. Das exakte Cyan gehört Logo und Ringen – als Textfarbe kommt es nie vor.", swatches: [
          ["Brand", "brand", "#039fba", "Logo, Jahresringe, Bedienelemente."],
          ["Brand link", "brand-link", "#006d81", "Links im Text."],
          ["Brand deep", "brand-deep", "#004553", "Aurora „Strong“: Term, Statement- und Display-Zitate. Hintergrund „Dark“."],
          ["Band", "band", "#94e6fb", "Das Kontaktband."],
          ["Band soft", "band-soft", "#bdeaf6", "Hintergrund „Accent“, Menüfläche."],
        ] },
        { title: "Kupfer", note: "Der Akzent. Fläche und Text sind zwei Stufen, damit beide lesbar bleiben.", swatches: [
          ["Copper", "copper", "#c64c00", "Schaltflächen."],
          ["Copper hover", "copper-hover", "#b43b00", "Schaltfläche unter dem Zeiger."],
          ["Copper text", "copper-text", "#a83500", "Aurora „Accent“: Kicker, Byline, Haken, Zähler, Link-Hover."],
          ["On copper", "on-copper", "#fefbf9", "Schrift auf Kupfer."],
        ] },
        { title: "Auf dunklem Grund", note: "Der Hintergrund „Dark“ tauscht die Tinten automatisch aus, damit Kicker und Zähler auf Petrol lesbar bleiben.", dark: true, swatches: [
          ["Ground", "ground", "#fafcfd", "Fließtext auf Dark."],
          ["Ground soft", "hero-ink-soft", "#dbebef", "„Soft“ auf Dark: Lede, Muted."],
          ["Copper light", "hero-copper", "#feb263", "„Accent“ auf Dark: Kicker, Zähler."],
          ["Rule light", "hero-rule", "#85adb5", "Linien auf Dark."],
        ] },
      ],
    },
    widths: {
      title: "Blockbreiten",
      intro: "„Block width“ in der Seitenleiste oder über die Breiten-Schaltfläche der Werkzeugleiste. Text steht auf „Narrow“, alles andere ist Layoutentscheidung.",
      entries: [
        ["Narrow", "Die Lesebreite von 66 Zeichen. Standard für jeden Textblock – und für die meisten der richtige."],
        ["Default", "Die Inhaltsspalte. Bilder, Tabellen, Teaser und Spaltengruppen."],
        ["Layout", "Die ganze Seitenspalte bis 76 rem. Für Listings und breite Spaltengruppen."],
        ["Full Width", "Randlos von Kante zu Kante. Für Bänder und den Hero; Textblöcken wird sie nicht angeboten."],
      ],
    },
    backgrounds: {
      title: "Hintergründe",
      intro: "„Background“ in der Seitenleiste. Ein Hintergrund macht aus Blöcken einen Abschnitt: aufeinanderfolgende Blöcke mit demselben Wert teilen sich ein Band.",
      entries: [
        { name: "none", label: "None", text: "Der Seitengrund. Der Normalfall." },
        { name: "grey", label: "Grey", text: "Surface. Ein ruhiger Abschnitt, etwa eine Übersicht unter dem Kapitel." },
        { name: "accent", label: "Accent", text: "Band soft. Ein Abschnitt, der Aufmerksamkeit verdient." },
        { name: "dark", label: "Dark", text: "Brand deep. Das Schlusskapitel. Text wird hell, Kicker und Zähler wechseln auf Copper light." },
      ],
      darkSample: { kicker: "Zum Mitnehmen", heading: "Drei Fragen vor dem nächsten Projekt", lede: "Wer sie beantworten kann, hat die Weichen gestellt.", questions: ["Wer kann die Anwendung in fünf Jahren weiterentwickeln?", "Welche Daten müssen exportierbar bleiben?"] },
      lightSample: { kicker: "Übersicht", heading: "Drei erprobte Grundlagen", lede: "Wir wählen Frameworks nach Prozess, Organisation und Lebensdauer der Anwendung." },
    },
    blocks: {
      title: "Blöcke",
      intro: "Was das Menü hinter <kbd>/</kbd> und die Seitenleiste anbieten.",
      groups: [
        { title: "Textblöcke", items: [
          ["Text", "Ein Absatz. Trägt die Textstile."],
          ["Heading 2 / 3 / 4", "Die Gliederung."],
          ["Bulleted list · Numbered list · To-do list", "Listen. Tragen die Listenstile."],
          ["Blockquote", "Ein Zitat. Trägt die Zitatstile."],
          ["Callout", "Ein hervorgehobener Hinweis mit Symbol."],
          ["Toggle", "Aufklappbarer Abschnitt, etwa für Details oder FAQ."],
          ["Code Block", "Mehrzeiliger Code mit Sprache."],
          ["Table", "Eine Tabelle."],
        ] },
        { title: "Plone-Blöcke", items: [
          ["Image · Video", "Medien mit Bildunterschrift."],
          ["Teaser", "Verweis auf eine andere Seite mit Bild, Titel und Beschreibung."],
          ["Listing", "Automatische Liste von Inhalten, etwa Vorträge oder Schulungen."],
          ["Table of contents", "Inhaltsverzeichnis aus den Überschriften."],
          ["Columns", "Spaltengruppe. Eine Spalte kann beim Scrollen haften („Sticky column“)."],
          ["Promo · Metadata · Actions", "Die Blöcke der derico-Seiten: Werbefläche, Metadaten und Handlungsaufrufe."],
        ] },
      ],
    },
  },
  en: {
    toc: "On this page",
    spec: { aurora: "In Aurora", font: "Type", color: "Colour", use: "Use" },
    how: {
      title: "How to format in Aurora",
      intro: "The design has a name for every role text can play. You pick the role; the theme supplies face, size and colour. Four moves cover it.",
      steps: [
        ["Insert a block", "Type <kbd>/</kbd> on an empty line. The “Text blocks” menu offers Text, Heading 2 to 4, lists, Toggle, Code Block, Table, Blockquote and Callout."],
        ["Change the block type", "Select some text and open “Turn into” in the floating toolbar: Text, Heading 2/3/4, Bulleted list, Numbered list, To-do list or Quote."],
        ["Pick a text style", "Select a word. “Text style” appears at the right end of the toolbar – “List style” on a list, “Quote style” on a quote. Top-level blocks show the same choice in the sidebar; inside columns only the toolbar reaches it."],
        ["Width and background", "Click a block and set “Block width” and “Background” in the sidebar. A background continues across consecutive blocks until one without it follows."],
      ],
      rulesTitle: "Principles",
      rules: [
        "A page has one title – the title block at the top. Headings start at Heading 2.",
        "Headings structure, they never enlarge. A line that needs size or colour takes a text style.",
        "“Normal” removes a style again. A block without a style looks the way it always did.",
        "Colours are never chosen directly. They come from style, background and theme, so every combination stays readable.",
        "Nothing below 15 pixels. There is no small print; hierarchy comes from weight, colour and spacing.",
      ],
    },
    fonts: {
      title: "Typefaces",
      intro: "Two typefaces carry the site. Both are self-hosted; nothing is loaded from third parties.",
      items: [
        ["Source Sans 3", "Body text, lists, navigation, byline, term", "The working face. 16 pixels at body size, line height 1.6."],
        ["Literata", "Headings, kicker, statement, quotes", "The display face, a reading font from book printing. Appears wherever a line should stand on its own."],
      ],
      sample: "Applications, grown to last. Sustainable solutions for more than twenty years – flexible, modern, secure.",
    },
    headings: {
      title: "Headings",
      intro: "Four levels, all in Literata. The level follows the outline, not the size you want.",
      entries: [
        { level: "title", sample: "Odoo connects your business processes.", aurora: "Title block (once per page)", font: "Literata 600 · 32–56 px", color: "Ink", use: "The page title. Filled from the page's title, not typed." },
        { level: "h2", sample: "What we build together", aurora: "Heading 2", font: "Literata 600 · 26–39 px", color: "Ink", use: "A chapter. The first level you set yourself." },
        { level: "h3", sample: "Responsibilities and response paths", aurora: "Heading 3", font: "Literata 600 · 22–28 px", color: "Ink", use: "A section within a chapter." },
        { level: "h4", sample: "Upgrade cycles", aurora: "Heading 4", font: "Source Sans 3 700 · 18 px", color: "Ink", use: "A run-in line in long sections. Sparingly." },
      ],
    },
    text: {
      title: "Text styles",
      intro: "The “Text style” menu on a paragraph. Seven roles, named for their job in the text.",
      entries: [
        { style: "normal", sample: "<p>We build business applications on Python, modern JavaScript and open source. Maintainability, open standards and clear decisions keep their value for many years.</p>", aurora: "Text style → Normal", font: "Source Sans 3 · 16 px · line height 1.6", color: "Ink", use: "Body text. The reading measure is 66 characters." },
        { style: "kicker", sample: "<p class=\"sg-kicker\">From practice</p><h2 class=\"sg-h2\">One association, three systems, one data model</h2>", aurora: "Text style → Kicker", font: "Literata italic · 16 px", color: "Accent (Copper text)", use: "The line above a heading or a statement. Binds to what follows: no space below it." },
        { style: "lede", sample: "<p class=\"sg-lede\">Technology is sound when it fits the task, stays understandable and can be developed reliably.</p>", aurora: "Text style → Lede", font: "Source Sans 3 · 18–22 px · line height 1.5", color: "Soft (Ink soft)", use: "The opening under a heading. One paragraph, rarely two." },
        { style: "statement", sample: "<p class=\"sg-statement\">An application is sustainable when someone still understands it ten years on.</p>", aurora: "Text style → Statement", font: "Literata · 18–22 px · line height 1.5", color: "Ink", use: "A claim that stands on its own – in a side column or closing a chapter. Up to 30 characters wide." },
        { style: "byline", sample: "<p class=\"sg-byline\">By Maik Derstappen</p>", aurora: "Text style → Byline", font: "Source Sans 3 700 · 16 px", color: "Accent (Copper text)", use: "The author line above the first paragraph of an article." },
        { style: "term", sample: "<p class=\"sg-term\">In service</p><p class=\"sg-muted\">Running since 2009, migrated three times, never rewritten.</p>", aurora: "Text style → Term", font: "Source Sans 3 700 · 16 px", color: "Strong (Brand deep)", use: "The term of a facts list. Binds to the paragraph below it, usually “Muted”." },
        { style: "muted", sample: "<p class=\"sg-muted\">Contact details and phone numbers are placeholders from the current site and are verified before publishing.</p>", aurora: "Text style → Muted", font: "Source Sans 3 · 16 px", color: "Soft (Ink soft)", use: "Quiet text: explanations, definitions, asides." },
      ],
    },
    lists: {
      title: "List styles",
      intro: "The “List style” menu on a list item. The style describes the whole list, not one item.",
      entries: [
        { style: "normal", sample: "<ul><li>Architecture, interface and operations planned as one task</li><li>Frameworks chosen by process and lifespan</li><li>Open standards instead of dependencies</li></ul>", aurora: "List style → Normal (Bulleted list, Numbered list, To-do list)", font: "Source Sans 3 · 16 px", color: "Ink", use: "The ordinary list. Numbered when order matters." },
        { style: "checklist", sample: "<ul class=\"sg-list sg-list--checklist\"><li>The source code is yours and lives in your repository.</li><li>Every dependency is openly licensed and actively maintained.</li><li>An upgrade path is written down before launch.</li></ul>", aurora: "List style → Checklist", font: "Source Sans 3 · 16 px · copper check mark", color: "Ink, mark Accent", use: "Criteria that are or should be met. No bullet, one check per row, a hairline above each." },
        { style: "questions", sample: "<ol class=\"sg-list sg-list--questions\"><li>Who can still develop the application in five years?</li><li>Which data must stay exportable – and in which format?</li><li>What happens if the vendor stops?</li></ol>", aurora: "List style → Questions", font: "Source Sans 3 · 16 px · counter in Literata 700", color: "Ink, counter Accent", use: "The take-away questions at the end of an article. Numbered, rules above each row and below the last." },
        { style: "sources", sample: "<ul class=\"sg-list sg-list--sources\"><li><a href=\"#\">Federal Ministry of the Interior: open-source strategy (2024)</a></li><li><a href=\"#\">Plone Foundation: release history</a></li></ul>", aurora: "List style → Sources", font: "Source Sans 3 · 16 px", color: "Soft (Ink soft)", use: "Sources and references. Quiet rows, links in soft ink." },
      ],
    },
    quotes: {
      title: "Quote styles",
      intro: "The “Quote style” menu on a blockquote.",
      entries: [
        { style: "normal", sample: "<blockquote class=\"sg-quote\">We choose frameworks by process, organisation and the lifespan of the application.</blockquote>", aurora: "Quote style → Normal (Blockquote)", font: "Source Sans 3 italic · 16 px", color: "Soft, rule Band rule", use: "A quotation in the run of the text. Rule on the left, italic." },
        { style: "statement", sample: "<blockquote class=\"sg-quote sg-quote--statement\">Software is sustainable when you can let it go without losing it.</blockquote>", aurora: "Quote style → Statement", font: "Literata 500 · 20–28 px · line height 1.4", color: "Strong (Brand deep), rule Band rule", use: "The thesis of an article. Rule on top, up to 36 characters wide." },
        { style: "display", sample: "<blockquote class=\"sg-quote sg-quote--display\">Public Money, Public Code.</blockquote>", aurora: "Quote style → Display", font: "Literata 650 · 28–48 px · line height 1.18", color: "Strong (Brand deep), rule Band rule", use: "A line as a poster. A few words, up to 22 characters wide. Once per page." },
      ],
    },
    marks: {
      title: "Inline marks",
      intro: "For words inside a paragraph. Select text, press the toolbar button. On Windows and Linux, Ctrl stands in for ⌘.",
      entries: [
        ["Bold", "<strong>Reliable care</strong> for applications that are needed every day.", "⌘ B", "A term that should catch a skimming eye. Never whole sentences."],
        ["Italic", "The word <em>sustainable</em> here means maintainability, not marketing.", "⌘ I", "Emphasis, foreign words, titles of works."],
        ["Strikethrough", "Response <s>within two working days</s> on the same working day.", "⌘ ⇧ M", "A correction that should stay visible. Rare."],
        ["Code", "The command <code>uv run pytest</code> runs the tests.", "⌘ E", "Commands, file names, identifiers."],
        ["Link", "More on <a href=\"#\">plone.org</a>.", "Link button", "References. The link text says where it goes – never “here”."],
      ],
    },
    colors: {
      title: "Colours",
      intro: "The “Jahresringe” palette: petrol as the brand, copper as the accent. Editorially you never pick a colour – every text style and background brings its own. The names in brackets are the tokens Aurora and the theme use.",
      groups: [
        { title: "Ground and text", note: "What every page carries.", swatches: [
          ["Ground", "ground", "#fafcfd", "The page ground."],
          ["Surface", "surface", "#ebf6f8", "A quiet surface. Background “Grey”."],
          ["Ink", "ink", "#101d22", "Body text, headings."],
          ["Ink soft", "ink-soft", "#31464e", "Aurora “Soft”: Lede, Muted, Sources."],
          ["Rule", "rule", "#b9cfd5", "Hairlines: Checklist, Questions."],
          ["Band rule", "band-rule", "#53838f", "Structural rules: quotes, bands."],
        ] },
        { title: "Petrol", note: "The brand. The exact cyan belongs to the logo and the rings – it never appears as a text colour.", swatches: [
          ["Brand", "brand", "#039fba", "Logo, growth rings, controls."],
          ["Brand link", "brand-link", "#006d81", "Links in text."],
          ["Brand deep", "brand-deep", "#004553", "Aurora “Strong”: Term, Statement and Display quotes. Background “Dark”."],
          ["Band", "band", "#94e6fb", "The contact band."],
          ["Band soft", "band-soft", "#bdeaf6", "Background “Accent”, menu panel."],
        ] },
        { title: "Copper", note: "The accent. Fill and text are two steps so both stay readable.", swatches: [
          ["Copper", "copper", "#c64c00", "Buttons."],
          ["Copper hover", "copper-hover", "#b43b00", "A button under the pointer."],
          ["Copper text", "copper-text", "#a83500", "Aurora “Accent”: Kicker, Byline, check marks, counters, link hover."],
          ["On copper", "on-copper", "#fefbf9", "Type on copper."],
        ] },
        { title: "On dark ground", note: "The “Dark” background swaps the inks automatically so kickers and counters stay readable on petrol.", dark: true, swatches: [
          ["Ground", "ground", "#fafcfd", "Body text on Dark."],
          ["Ground soft", "hero-ink-soft", "#dbebef", "“Soft” on Dark: Lede, Muted."],
          ["Copper light", "hero-copper", "#feb263", "“Accent” on Dark: Kicker, counters."],
          ["Rule light", "hero-rule", "#85adb5", "Rules on Dark."],
        ] },
      ],
    },
    widths: {
      title: "Block widths",
      intro: "“Block width” in the sidebar, or the width button in the toolbar. Text sits on “Narrow”; everything else is a layout decision.",
      entries: [
        ["Narrow", "The reading measure of 66 characters. Default for every text block – and the right one for most."],
        ["Default", "The content column. Images, tables, teasers and column groups."],
        ["Layout", "The whole page column up to 76 rem. For listings and wide column groups."],
        ["Full Width", "Edge to edge. For bands and the hero; text blocks are not offered it."],
      ],
    },
    backgrounds: {
      title: "Backgrounds",
      intro: "“Background” in the sidebar. A background turns blocks into a section: consecutive blocks with the same value share one band.",
      entries: [
        { name: "none", label: "None", text: "The page ground. The usual case." },
        { name: "grey", label: "Grey", text: "Surface. A quiet section, such as an overview under a chapter." },
        { name: "accent", label: "Accent", text: "Band soft. A section that deserves attention." },
        { name: "dark", label: "Dark", text: "Brand deep. The closing chapter. Text turns light; kickers and counters switch to Copper light." },
      ],
      darkSample: { kicker: "Take-away", heading: "Three questions before the next project", lede: "Whoever can answer them has set the course.", questions: ["Who can develop the application in five years?", "Which data must stay exportable?"] },
      lightSample: { kicker: "Overview", heading: "Three proven foundations", lede: "We choose frameworks by process, organisation and the lifespan of the application." },
    },
    blocks: {
      title: "Blocks",
      intro: "What the menu behind <kbd>/</kbd> and the sidebar offer.",
      groups: [
        { title: "Text blocks", items: [
          ["Text", "A paragraph. Carries the text styles."],
          ["Heading 2 / 3 / 4", "The outline."],
          ["Bulleted list · Numbered list · To-do list", "Lists. Carry the list styles."],
          ["Blockquote", "A quotation. Carries the quote styles."],
          ["Callout", "A highlighted note with an icon."],
          ["Toggle", "A collapsible section, for details or FAQ."],
          ["Code Block", "Multi-line code with a language."],
          ["Table", "A table."],
        ] },
        { title: "Plone blocks", items: [
          ["Image · Video", "Media with a caption."],
          ["Teaser", "A reference to another page with image, title and description."],
          ["Listing", "An automatic list of content, such as talks or training."],
          ["Table of contents", "Generated from the headings."],
          ["Columns", "A column group. One column can stick while scrolling (“Sticky column”)."],
          ["Promo · Metadata · Actions", "The derico blocks: promotional band, metadata and calls to action."],
        ] },
      ],
    },
  },
};

const sgSpec = (t, rows) => `<dl class="sg-spec">${rows.map(([key, value]) => `<div><dt>${t.spec[key]}</dt><dd>${value}</dd></div>`).join("")}</dl>`;
const sgEntry = (t, name, sample, spec, modifier = "") => `<div class="sg-entry${modifier}"><div class="sg-entry__sample">${sample}</div><div class="sg-entry__meta"><h3 class="sg-entry__name">${name}</h3>${sgSpec(t, spec)}</div></div>`;
const sgSection = (id, title, intro, body) => `<section class="sg-section" id="${id}"><h2 class="section-heading">${title}</h2><p class="section-intro">${intro}</p>${body}</section>`;
const sgStyled = (level, text) => level === "title" ? `<h1 class="sg-h1">${text}</h1>` : `<${level} class="sg-${level}">${text}</${level}>`;

function renderStyleguide(lang, page) {
  const t = styleguideCopy[lang];
  const sections = ["how", "fonts", "headings", "text", "lists", "quotes", "marks", "colors", "widths", "backgrounds", "blocks"];
  const toc = `<nav class="sg-toc" aria-label="${t.toc}"><p class="page-context">${t.toc}</p><ol>${sections.map((id) => `<li><a href="#${id}">${t[id].title}</a></li>`).join("")}</ol></nav>`;

  const how = sgSection("how", t.how.title, t.how.intro, `<ol class="sg-steps">${t.how.steps.map(([title, text]) => `<li><strong>${title}</strong><span>${text}</span></li>`).join("")}</ol><h3 class="sg-subheading">${t.how.rulesTitle}</h3><ul class="sg-list sg-list--checklist">${t.how.rules.map((rule) => `<li>${rule}</li>`).join("")}</ul>`);

  const fonts = sgSection("fonts", t.fonts.title, t.fonts.intro, `<div class="sg-fonts">${t.fonts.items.map(([name, roles, text]) => `<div class="sg-font sg-font--${name === "Literata" ? "display" : "body"}"><p class="sg-font__sample" lang="${lang}">${t.fonts.sample}</p><h3>${name}</h3><p class="sg-term">${roles}</p><p class="sg-muted">${text}</p></div>`).join("")}</div>`);

  const headings = sgSection("headings", t.headings.title, t.headings.intro, t.headings.entries.map((e) => sgEntry(t, e.aurora, sgStyled(e.level, e.sample), [["font", e.font], ["color", e.color], ["use", e.use]])).join(""));

  const styled = (key) => sgSection(key, t[key].title, t[key].intro, t[key].entries.map((e) => sgEntry(t, e.aurora, e.sample, [["font", e.font], ["color", e.color], ["use", e.use]])).join(""));

  const marks = sgSection("marks", t.marks.title, t.marks.intro, `<div class="sg-table-wrap"><table class="sg-table"><thead><tr><th>${t.spec.aurora}</th><th>${lang === "de" ? "Beispiel" : "Example"}</th><th>${lang === "de" ? "Tastatur" : "Keyboard"}</th><th>${t.spec.use}</th></tr></thead><tbody>${t.marks.entries.map(([name, sample, keys, use]) => `<tr><th scope="row">${name}</th><td>${sample}</td><td><kbd>${keys}</kbd></td><td>${use}</td></tr>`).join("")}</tbody></table></div>`);

  const colors = sgSection("colors", t.colors.title, t.colors.intro, t.colors.groups.map((group) => `<div class="sg-palette${group.dark ? " sg-palette--dark" : ""}"><h3 class="sg-subheading">${group.title}</h3><p class="sg-muted">${group.note}</p><ul class="sg-swatches">${group.swatches.map(([name, token, hex, role]) => `<li><span class="sg-swatch" style="--sg-swatch: var(--${token})"></span><strong>${name}</strong><code>--${token} · ${hex}</code><span>${role}</span></li>`).join("")}</ul></div>`).join(""));

  const widths = sgSection("widths", t.widths.title, t.widths.intro, `<div class="sg-widths" aria-hidden="true">${["full", "layout", "default", "narrow"].map((w) => `<div class="sg-width sg-width--${w}"><span>${t.widths.entries.find(([label]) => label.toLowerCase().startsWith(w))[0]}</span></div>`).join("")}</div><dl class="sg-spec sg-spec--row">${t.widths.entries.map(([label, text]) => `<div><dt>${label}</dt><dd>${text}</dd></div>`).join("")}</dl>`);

  const dark = t.backgrounds.darkSample;
  const light = t.backgrounds.lightSample;
  const bandInner = (s) => `<p class="sg-kicker">${s.kicker}</p><h3 class="sg-h3">${s.heading}</h3><p class="sg-lede">${s.lede}</p>`;
  const backgrounds = sgSection("backgrounds", t.backgrounds.title, t.backgrounds.intro, `<div class="sg-bands">${t.backgrounds.entries.map((b) => `<div class="sg-band sg-band--${b.name}"><p class="sg-band__label"><strong>${b.label}</strong> <span>${b.text}</span></p>${b.name === "dark" ? `${bandInner(dark)}<ol class="sg-list sg-list--questions">${dark.questions.map((q) => `<li>${q}</li>`).join("")}</ol>` : bandInner(light)}</div>`).join("")}</div>`);

  const blocks = sgSection("blocks", t.blocks.title, t.blocks.intro, `<div class="sg-blocks">${t.blocks.groups.map((group) => `<div><h3 class="sg-subheading">${group.title}</h3><dl class="sg-spec sg-spec--row">${group.items.map(([label, text]) => `<div><dt>${label}</dt><dd>${text}</dd></div>`).join("")}</dl></div>`).join("")}</div>`);

  return `${pageHero(page)}<div class="shell sg">${toc}<div class="sg-body">${how}${fonts}${headings}${styled("text")}${styled("lists")}${styled("quotes")}${marks}${colors}${widths}${backgrounds}${blocks}</div></div>`;
}

function renderBody(lang, page) {
  if (page.type === "home") return renderHome(lang, page);
  if (page.type === "overview") return renderOverview(lang, page);
  if (page.type === "detail") return renderDetail(lang, page);
  if (page.type === "sustainability") return renderSustainability(lang, page);
  if (page.type === "training") return renderTraining(lang, page);
  if (page.type === "talks") return renderTalks(lang, page);
  if (page.type === "contact") return renderContact(lang, page);
  if (page.type === "imprint") return renderImprint(lang, page);
  if (page.type === "styleguide") return renderStyleguide(lang, page);
  throw new Error(`Unknown page type: ${page.type}`);
}

function document(lang, key, page) {
  const description = page.lede.replace(/<[^>]+>/g, "");
  const includeContact = !["contact", "imprint", "styleguide"].includes(key);
  const heroPreload = key === "home" ? `
  <link rel="preload" as="image" href="../assets/images/hero-managed-forest-portrait-720.avif" imagesrcset="../assets/images/hero-managed-forest-portrait-720.avif 720w, ../assets/images/hero-managed-forest-portrait-1080.avif 1080w" imagesizes="100vw" type="image/avif" media="(max-width: 55.99rem)">
  <link rel="preload" as="image" href="../assets/images/hero-managed-forest-wide-1600.avif" imagesrcset="../assets/images/hero-managed-forest-wide-960.avif 960w, ../assets/images/hero-managed-forest-wide-1600.avif 1600w, ../assets/images/hero-managed-forest-wide-2400.avif 2400w" imagesizes="100vw" type="image/avif" media="(min-width: 56rem)">` : "";
  return `<!doctype html>
<html lang="${lang}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <meta name="description" content="${description}">
  <meta name="theme-color" content="#fafcfd">
  <title>${page.title} · derico</title>
  <link rel="preload" href="../assets/fonts/source-sans-3-latin-wght-normal.woff2" as="font" type="font/woff2" crossorigin>${heroPreload}
  <link rel="stylesheet" href="../assets/site.css">
  <script>document.documentElement.classList.add("js")</script>
  <script src="../assets/site.js" defer></script>
</head>
<body>
  ${header(lang, key)}
  ${breadcrumbs(lang, key, page.context.split(" · ").at(-1))}
  <main id="main">${renderBody(lang, page)}</main>
  ${subnav(lang, page)}
  ${includeContact ? contactBand(lang, page) : ""}
  ${footer(lang)}
</body>
</html>`;
}

for (const lang of ["de", "en"]) {
  await mkdir(join(root, lang), { recursive: true });
  for (const [key, page] of Object.entries(pages[lang])) {
    await writeFile(join(root, lang, slugs[lang][key]), document(lang, key, page));
  }
  const isDe = lang === "de";
  const errorDocument = `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover"><title>${isDe ? "Seite nicht gefunden" : "Page not found"} · derico</title><link rel="stylesheet" href="../assets/site.css"><script>document.documentElement.classList.add("js")</script><script src="../assets/site.js" defer></script></head><body>${header(lang, "home")}<main id="main" class="error-page"><div class="shell error-page__inner"><p class="error-page__code">404</p><h1>${isDe ? "Diese Seite ist nicht mehr hier." : "This page is no longer here."}</h1><p>${isDe ? "Die Adresse kann veraltet sein. Über die Leistungen oder die Startseite finden Sie einen neuen Weg." : "The address may be outdated. Services or the home page will give you a current route."}</p><div class="action-row"><a class="button" href="${href(lang, "home")}">${isDe ? "Zur Startseite" : "Go to home"}</a><a class="quiet-link" href="${href(lang, "services")}">${navigation[lang].services.overview}</a></div></div></main>${footer(lang)}</body></html>`;
  await writeFile(join(root, lang, "404.html"), errorDocument);
}

await writeFile(join(root, "index.html"), `<!doctype html><html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta http-equiv="refresh" content="0; url=de/index.html"><title>derico</title></head><body><p><a href="de/index.html">derico.de öffnen</a> · <a href="en/index.html" lang="en">Open derico.de in English</a></p></body></html>`);

console.log(`Built ${Object.keys(pages.de).length * 2 + 3} static documents in ${root}`);
