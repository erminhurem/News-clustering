# Pomoćna funkcija za pretvaranje URL-a izvora u prijateljsko ime
def get_friendly_source_name(url):
    if 'telegraf.rs' in url:
        return 'Telegraf'
    elif 'kurir.rs' in url:
        return 'Kurir'
    elif 'www.euronews.rs' in url:
        return 'Euronews'
    elif 'nova.rs' in url:
        return 'Nova'
    elif 'n1info.ba' in url:
        return 'N1'
    elif 'n1info.hr' in url:
        return 'N1'
    elif 'klix.ba' in url:
        return 'Klix'
    elif 'balkans.aljazeera.net' in url:
        return 'Aljazeera'
    elif 'avaz.ba' in url:
        return 'Dnevni avaz'
    elif 'okanal.oslobodjenje.ba/okanal' in url:
        return 'Okanal'
    elif 'oslobodjenje.ba' in url:
        return 'Oslobodjenje'
    elif 'alo.rs' in url:
        return 'Alo'
    elif '24sata.hr' in url:
        return '24sata'
    elif 'vecernji.hr' in url:
        return 'Vecernji'
    elif 'sd.rs' in url:
        return 'SD'
    elif 'blic.rs' in url:
        return 'Blic'
    elif 'mondo.ba' in url:
        return 'Mondo'
    elif 'mondo.rs' in url:
        return 'Mondo'
    elif 'namaz.ba' in url:
        return 'Namaz'
    elif 'b92.net' in url:
        return 'B92'
    elif 'espreso.co.rs' in url:
        return 'Espreso'
    elif 'vijesti.ba' in url:
        return 'Vijesti'
    elif 'informer.rs' in url:
        return 'Informer'
    elif 'beta.rs' in url:
        return 'Beta'
    elif 'oslobodjenje.ba' in url:
        return 'Oslobodjenje'
    elif 'nkp.ba' in url:
        return 'NKP'
    elif 'rtvslon.ba' in url:
        return 'Slon'
    elif 'rts.rs' in url:
        return 'RTS'
    elif 'slobodna-bosna.ba' in url:
        return 'Slobodna Bosna'
    elif 'radiosarajevo.ba' in url:
        return 'Radio Sarajevo'
    elif 'report.ba' in url:
        return 'Report'
    elif 'bikemagazin.info' in url:
        return 'Bikemagazin'
    elif 'profitiraj.ba' in url:
        return 'Profitiraj'
    elif 'yep.ba' in url:
        return 'Yep'
    elif 'biznis.ba' in url:
        return 'Biznis'
    elif 'carlander.ba' in url:
        return 'Carlander'
    elif 'auto.ba' in url:
        return 'Auto'
    elif 'lifestyle.ba' in url:
        return 'Lifestyle'
    elif 'ljepotaizdravlje.ba' in url:
        return 'Ljepota i zdravlje'
    elif 'reprezentacija.ba' in url:
        return 'Reprezentacija'
    elif 'sportske.ba' in url:
        return 'Sportske'
    elif 'scsport.ba' in url:
        return 'Scsport'
    elif 'senzacija.ba' in url:
        return 'Senzacija'
    elif 'zdraviportal.ba' in url:
        return 'Zdravi portal'
    elif '24h.ba' in url:
        return '24h'
    elif 'pogled.ba' in url:
        return 'Pogled'
    elif 'bosnainfo.ba' in url:
        return 'Bosnainfo'
    elif 'caportal.net' in url:
        return 'Car portal'
    elif 'sirokibrijeg.info' in url:
        return 'Siroki Brijeg'
    elif 'dnevni.ba' in url:
        return 'Dnevni'
    elif 'jabuka.tv' in url:
        return 'Jabuka'
    elif 'novasloboda.ba' in url:
        return 'Nova Sloboda'
    elif 'mostarski.info' in url:
        return 'Mostarski'
    elif 'blmojgrad.com' in url:
        return 'BL'
    elif 'bl-portal.com' in url:
        return 'BL portal'
    elif 'tip.ba' in url:
        return 'Tip'
    elif 'zepce.live' in url:
        return 'Zepce'
    elif 'zenit.ba' in url:
        return 'Zenit'
    elif '072info.com' in url:
        return '072Info'
    elif 'zenicablog.com' in url:
        return 'Zenica blog'
    elif 'cazin.ba' in url:
        return 'Cazin'
    elif 'hercegovina.info' in url:
        return 'Hercegovina'
    elif 'ilijas.net' in url:
        return 'Ilijas'
    elif 'detektor.ba' in url:
        return 'Detektor'
    elif 'tuzlalive.ba' in url:
        return 'Tulalive'
    elif 'capital.ba' in url:
        return 'Capital'
    elif 'poskok.info' in url:
        return 'Poskok'
    elif 'biznisinfo.ba' in url:
        return 'Biznisinfo'
    elif 'pressmediabih.com' in url:
        return 'Pressmediabih'
    elif 'politicki.ba' in url:
        return 'Politicki'
    elif 'thebosniatimes.ba' in url:
        return 'Thebosniatimes'
    elif 'krajina.ba' in url:
        return 'Krajina'
    elif 'akta.ba' in url:
        return 'Akta'
    elif 'centralna.ba' in url:
        return 'Centrala'
    elif 'otisak.ba' in url:
        return 'Otisak'
    elif 'times.ba' in url:
        return 'Times'
    elif 'azra.ba' in url:
        return 'Azra'
    elif 'jajce-online.com' in url:
        return 'Jajceonline'
    elif 'izdvojeno.ba' in url:
        return 'Izdvojeno'
    elif 'bljesak.info' in url:
        return 'Bljesak'
    elif 'tuzlanski.ba' in url:
        return 'Tuzlanski'
    elif 'crna-hronika.info' in url:
        return 'Crnahronika'
    elif 'p-portal.ne' in url:
        return 'P-portal'
    elif 'sportsport.ba' in url:
        return 'Sportsport'
    elif 'haber.ba' in url:
        return 'Haber'
    elif 'arhiv.stav.ba' in url:
        return 'Stav'
    elif 'istraga.ba' in url:
        return 'Istraga'
    elif 'vecernji.ba' in url:
        return 'Vecernji'
    elif 'dnevnik.ba' in url:
        return 'Dnevnik'
    elif 'raport.ba' in url:
        return 'Raport'
    elif 'bhportal.ba' in url:
        return 'Bhportal'
    elif 'fokus.ba' in url:
        return 'Fokus'
    elif 'hayat.ba' in url:
        return 'Hayat'
    elif 'gracanicki.ba' in url:
        return 'Gracanicki'
    elif 'visoko.ba' in url:
        return 'Visoko'
    elif 'magazinplus.eu' in url:
        return 'Magazinplus'
    elif 'visocki.info' in url:
        return 'Visocki'
    elif 'gorazdeportal.com' in url:
        return 'Gorazdeportal'
    elif 'direkt-portal.com' in url:
        return 'Direktportal'
    elif 'ljportal.com' in url:
        return 'Ljportal'
    elif 'grad-busovaca.com' in url:
        return 'Grad Busovaca'
    elif 'federalna.ba' in url:
        return 'Federalna'
    elif 'zepce.ba' in url:
        return 'Zepce'
    elif 'brckodanas.com' in url:
        return 'Brckodanas'
    elif 'granicedoboja.info' in url:
        return 'Granicedoboja'
    elif 'sop.ba' in url:
        return 'Sop'
    elif 'novabh.tv' in url:
        return 'Novabh'
    elif 'rtcg.me' in url:
        return 'RTCG'
    elif 'mondo.me' in url:
        return 'Mondo'
    elif 'vijesti.me' in url:
        return 'Vijesti'
    elif 'lepotaizdravlje.rs' in url:
        return 'Ljepotaizdravlje'
    elif 'danas.rs' in url:
        return 'Danas'
    elif 'svet-scandal.rs' in url:
        return 'Svet-scandal'
    elif 'tanjug.rs' in url:
        return 'Tanjug'
    elif 'republika.rs' in url:
        return 'Rpublika'
    elif 'politika.rs' in url:
        return 'Politika'
    elif 'euronews.rs' in url:
        return 'Euronews'
    elif 'b92.net' in url:
        return 'B92'
    elif 'journal.hr' in url:
        return 'Jurnal'
    elif 'vecernji.hr' in url:
        return 'Vecernji'
    elif 'dnevno.hr' in url:
        return 'Dneveno'
    elif 'slobodnadalmacija.hr' in url:
        return 'Slobodnadalmacija'
    elif 'n1info.hr' in url:
        return 'N1'
    elif 'gloria.hr' in url:
        return 'Gloria'
    elif 'novilist.hr' in url:
        return 'Novilist'
    elif 'tportal.hr' in url:
        return 'Tportal'
    elif '24sata.hr' in url:
        return '24sata'
    elif 'dnevnik.hr' in url:
        return 'Dnevnik'
    elif 'jutarnji.hr' in url:
        return 'Jutarnji'
    elif 'telegram.hr' in url:
        return 'Telegram'
    elif 'net.hr' in url:
        return 'Net'
    elif 'index.hr' in url:
        return 'Index'
    else:
        return 'Nepoznati izvor'