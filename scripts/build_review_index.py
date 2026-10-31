"""Genera un índice estático y autocontenido de lectura, sin dependencias externas.

Ejecutar desde la raíz: python scripts/build_review_index.py
El índice también funciona al abrir index.html directamente desde una carpeta.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
GITHUB = 'https://github.com/schubertlombeida/RAG.SALVAGUARDAS.GLF.UEES'
DOCS = [
    ('planificacion', '01_Planificacion_RAG_GLF', 'Planificación', 'Problema, usuarios, objetivos, alcance y organización del proyecto.'),
    ('analisis_datos', '02_Analisis_de_datos_RAG_GLF', 'Análisis de datos', 'Fuentes, preparación del corpus, análisis exploratorio y visualizaciones.'),
    ('arquitectura', '03_Arquitectura_RAG_GLF', 'Arquitectura', 'Cómo se conectan el portal, los modelos y los servicios de recuperación.'),
    ('optimizacion', '04_Optimizacion_RAG_GLF', 'Optimización y evaluación', 'Experimentos, resultados, pruebas y alcance de las mediciones.'),
    ('consideraciones_eticas', '05_Consideraciones_eticas_RAG_GLF', 'Consideraciones éticas', 'Privacidad, sesgos, explicabilidad y responsabilidad humana.'),
    ('manual_usuario', '06_Manual_de_usuario_RAG_GLF', 'Manual de uso', 'Acceso, consultas, fuentes, modelos, historial y manejo de errores.'),
    ('guia_entrega_y_videos', '07_Guia_de_entrega_y_videos_RAG_GLF', 'Guía de revisión', 'Recorrido de la entrega y correspondencia con los criterios de evaluación.'),
]

def esc(text):
    return html.escape(str(text), quote=True)

def inline(text):
    # Subconjunto Markdown utilizado por los informes; todo texto se escapa.
    slots = []
    def reserve(value):
        slots.append(value)
        return f'@@SLOT{len(slots)-1}@@'
    def link(m):
        target = m.group(2)
        if not re.match(r'^(https?://|\.\./|[\w./#-]+$)', target):
            return m.group(1)
        target = target.removeprefix('../')
        extra = ' target="_blank" rel="noopener noreferrer"' if target.startswith('http') else ''
        return reserve(f'<a href="{esc(target)}"{extra}>{esc(m.group(1))}</a>')
    text = re.sub(r'`([^`]+)`', lambda m: reserve('<code>'+esc(m.group(1))+'</code>'), text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', link, text)
    def raw_url(m):
        url = m.group().rstrip('.,;:!?)')
        suffix = m.group()[len(url):]
        return reserve(f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(url)}</a>') + suffix
    text = re.sub(r'https?://[^\s<>]+', raw_url, text)
    text = esc(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    for n, value in enumerate(slots):
        text = text.replace(f'@@SLOT{n}@@', value)
    return text

def markdown(source):
    lines = source.splitlines()
    parts = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('```'):
            code = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i]); i += 1
            parts.append('<pre><code>'+esc('\n'.join(code))+'</code></pre>'); i += 1
            continue
        image = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
        if image:
            target = image.group(2).removeprefix('../')
            if not (ROOT / target).is_file():
                raise FileNotFoundError(target)
            parts.append(f'<figure><a href="{esc(target)}" target="_blank" rel="noopener"><img loading="lazy" src="{esc(target)}" alt="{esc(image.group(1))}"></a><figcaption>{esc(image.group(1))}. Seleccione la imagen para ampliarla.</figcaption></figure>')
            i += 1; continue
        if line.startswith('#'):
            level = min(len(line)-len(line.lstrip('#')), 3)+1
            parts.append(f'<h{level}>{inline(line.lstrip("# "))}</h{level}>'); i += 1; continue
        if line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                cells = [x.strip() for x in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', x) for x in cells):
                    rows.append(cells)
                i += 1
            table = '<div class="table-scroll" tabindex="0" role="region" aria-label="Tabla del informe"><table><thead><tr>'
            table += ''.join('<th scope="col">'+inline(x)+'</th>' for x in rows[0])+'</tr></thead><tbody>'
            table += ''.join('<tr>'+''.join('<td>'+inline(x)+'</td>' for x in row)+'</tr>' for row in rows[1:])
            parts.append(table+'</tbody></table></div>'); continue
        if re.match(r'^(\d+\. |[-*] )', line):
            ordered = bool(re.match(r'^\d+\.', line))
            tag = 'ol' if ordered else 'ul'
            items = []
            pattern = r'^\d+\. ' if ordered else r'^[-*] '
            while i < len(lines) and re.match(pattern, lines[i].strip()):
                items.append('<li>'+inline(re.sub(pattern, '', lines[i].strip()))+'</li>'); i += 1
            parts.append(f'<{tag}>'+''.join(items)+f'</{tag}>'); continue
        paragraph = [line]; i += 1
        while i < len(lines) and lines[i].strip() and not re.match(r'^(#|\||!\[|```|\d+\. |[-*] )', lines[i].strip()):
            paragraph.append(lines[i].strip()); i += 1
        parts.append('<p>'+inline(' '.join(paragraph))+'</p>')
    return '\n'.join(parts)

def build():
    cards, articles, outline, search = [], [], [], []
    for n, (slug, filename, title, description) in enumerate(DOCS, 1):
        source = (ROOT/'docs'/f'{slug}.md').read_text(encoding='utf-8')
        word, pdf = f'entregables/{filename}.docx', f'entregables/{filename}.pdf'
        github = f'{GITHUB}/blob/main/docs/{slug}.md'
        links = f'<a href="{word}" download>Word <span class="sr-only">de {esc(title)}</span></a><a href="{pdf}" target="_blank" rel="noopener">PDF <span class="sr-only">de {esc(title)}</span></a><a href="{github}" target="_blank" rel="noopener noreferrer">GitHub <span class="sr-only">de {esc(title)}</span> ↗</a>'
        cards.append(f'<article class="doc-card" data-card="{slug}"><div class="card-number">{n:02d} / INFORME</div><h3>{esc(title)}</h3><p>{esc(description)}</p><a class="read-link" href="#informe={slug}">Leer informe <span aria-hidden="true">→</span></a><div class="file-links">{links}</div></article>')
        articles.append(f'<article class="report" id="report-{slug}" data-report="{slug}" hidden><div class="report-actions">{links}<button type="button" data-print>Imprimir</button></div>{markdown(source)}</article>')
        outline.append(f'<a href="#informe={slug}" data-outline="{slug}"><span>{n:02d}</span> {esc(title)}</a>')
        search.append(dict(id=slug, title=title, description=description, text=source))
    resources = [('Código fuente', 'tree/main/src', 'Recuperación, preparación y evaluación'), ('Cuadernos', 'tree/main/notebooks', 'Cinco cuadernos de análisis reproducible'), ('Pruebas y evidencia', 'tree/main/results', 'Figuras, métricas y consultas documentadas'), ('Evaluación reproducible', 'tree/main/evaluation', 'Protocolo de anotación y comparación'), ('Datos y modelos', 'tree/main/data', 'Fuentes públicas y preparación del corpus'), ('Integración GLF', 'tree/main/integration', 'Componentes y trazabilidad del portal')]
    resource_html = ''.join(f'<a href="{GITHUB}/{path}" target="_blank" rel="noopener noreferrer"><span>{title} ↗</span><small>{desc}</small></a>' for title, path, desc in resources)
    shell = '''<!doctype html>
<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="description" content="Entrega académica del Grupo 10: asistente RAG de salvaguardas del Galápagos Life Fund. Informes, código, evaluación y acceso al portal."><meta name="color-scheme" content="light"><title>RAG de salvaguardas GLF · Grupo 10</title><link rel="stylesheet" href="assets/review.css"><script src="assets/videos.js" defer></script><script src="assets/review.js" defer></script></head>
<body><a class="skip-link" href="#main">Saltar al contenido</a>
<header class="site-header"><div class="header-inner"><a class="brand" href="#documentacion" aria-label="RAG GLF, inicio"><span class="brand-mark" aria-hidden="true">R</span><span>RAG / GLF<small>PROYECTO INTEGRADOR · GRUPO 10</small></span></a><nav aria-label="Menú principal"><a href="#documentacion" data-main="documentacion">Documentación</a><a href="#portal" data-main="portal">Portal GLF <span aria-hidden="true">↗</span></a></nav></div></header>
<main id="main" tabindex="-1">
<section id="documentation-view"><div class="hero"><p class="eyebrow">INTELIGENCIA ARTIFICIAL APLICADA · UEES</p><h1>Evidencia documental para<br>las salvaguardas del GLF</h1><p class="lead">Un asistente de generación aumentada por recuperación (RAG) que conecta las consultas con sus fuentes. Explore la documentación académica y pruebe la implementación en el Galápagos Life Fund.</p><p class="authors">Schubert Lombeida Manjarrez · Niko Dimitri Jiménez Bruno</p><div class="hero-actions"><a class="button primary" href="#informe=manual_usuario">Comenzar por el manual <span aria-hidden="true">→</span></a><a class="button secondary" href="__GITHUB__" target="_blank" rel="noopener noreferrer">Abrir repositorio ↗</a></div><div class="edition">EDICIÓN · 30 OCT 2026 <span>Servicio RAG · glf-grounded-v3.1</span></div></div>
<section class="documents-section" aria-labelledby="docs-title"><div class="section-heading"><div><p class="eyebrow">LA ENTREGA</p><h2 id="docs-title">Informes y documentación</h2></div><p>Lea aquí o descargue la versión que prefiera.</p></div><form class="search" role="search"><label for="document-search">Buscar en los siete informes</label><div class="search-input"><input id="document-search" type="search" placeholder="Por ejemplo: modelos, métricas o manejo de errores" autocomplete="off"><button type="reset">Limpiar</button></div><p id="search-status" aria-live="polite" role="status">7 informes disponibles</p></form><div class="document-grid">__CARDS__</div><p class="empty-state" id="no-results" hidden>No se encontraron informes con esos términos. Pruebe otra palabra o limpie la búsqueda.</p></section>
<section class="resource-section" aria-labelledby="resources-title"><div class="section-heading"><div><p class="eyebrow">REPRODUCIBILIDAD</p><h2 id="resources-title">Código y evidencia</h2></div></div><div class="resource-grid">__RESOURCES__</div></section>
<section id="video-section" aria-labelledby="video-title" hidden><div class="section-heading"><div><p class="eyebrow">PRESENTACIÓN DEL EQUIPO</p><h2 id="video-title">Videos del proyecto</h2></div></div><div id="video-cards" class="video-grid"></div></section></section>
<section id="reader-view" hidden><div class="reader-top"><a class="back-link" href="#documentacion">← Todos los informes</a><span>LECTURA DE LA ENTREGA</span></div><div class="reader-layout"><aside class="reader-sidebar"><h2>Contenido</h2><nav aria-label="Informes de la entrega">__OUTLINE__</nav></aside><div class="reader-content" tabindex="-1">__ARTICLES__<nav class="reader-pagination" aria-label="Informe anterior y siguiente"><a id="previous-report" href="#documentacion">← Anterior</a><a id="next-report" href="#documentacion">Siguiente →</a></nav></div></div></section>
<section id="portal-view" hidden><div class="portal-intro"><p class="eyebrow">IMPLEMENTACIÓN PUBLICADA</p><h1 tabindex="-1">Pruebe el asistente en el portal GLF</h1><p class="lead">Consulte evidencia normativa, revise las fuentes y observe qué modelo interviene en cada etapa.</p></div><div class="portal-layout"><div class="portal-panel"><h2>Acceso al asistente</h2><ol class="access-steps"><li>Abra el asistente e inicie sesión con la cuenta de evaluación.</li><li>Elija consulta libre y seleccione una respuesta con fuentes o una búsqueda de fragmentos.</li><li>Escriba su pregunta, observe el procesamiento y abra las referencias de la respuesta.</li></ol><p class="access-note">Las credenciales se comparten por el portal de la universidad. Este índice no solicita ni almacena contraseñas.</p><a class="button primary" href="https://glf-postulaciones.vercel.app/internal/evidence" target="_blank" rel="noopener noreferrer">Abrir el asistente ↗</a><a class="portal-home" href="https://glf-postulaciones.vercel.app/" target="_blank" rel="noopener noreferrer">Ir al inicio del portal GLF ↗</a></div><div class="portal-context"><h2>Un recorrido breve</h2><p>Pruebe una consulta como «¿Qué es un PGAS?». Compare los modos breve y ampliado y compruebe la respuesta en el documento original.</p><div class="route"><span>01</span><div><h3>Pregunta</h3><p>Una consulta concreta sobre salvaguardas.</p></div></div><div class="route"><span>02</span><div><h3>Evidencia y modelo</h3><p>El sistema recupera pasajes e informa la etapa y el tiempo transcurrido.</p></div></div><div class="route"><span>03</span><div><h3>Fuentes y revisión</h3><p>La decisión técnica permanece en manos del especialista.</p></div></div><a class="read-link" href="#informe=manual_usuario">Consultar el manual de uso →</a></div></div></section>
</main><footer class="site-footer"><span>Grupo 10 · Proyecto integrador de inteligencia artificial</span><a href="__GITHUB__" target="_blank" rel="noopener noreferrer">Documentación y código en GitHub ↗</a></footer><script id="document-catalog" type="application/json">__CATALOG__</script><noscript><div class="noscript">Para leer dentro de este índice active JavaScript. Los enlaces Word, PDF y GitHub de cada informe funcionan directamente.</div></noscript></body></html>'''
    replacements = {'__GITHUB__': GITHUB, '__CARDS__': '\n'.join(cards), '__OUTLINE__': '\n'.join(outline), '__ARTICLES__': '\n'.join(articles), '__RESOURCES__':resource_html, '__CATALOG__':json.dumps(search, ensure_ascii=False).replace('<', '\\u003c')}
    for key, value in replacements.items():
        shell = shell.replace(key, value)
    (ROOT/'index.html').write_text(shell, encoding='utf-8')
    catalog_js = (ROOT/'assets/videos.js').read_text(encoding='utf-8')
    video_entries = json.loads(catalog_js.split('window.GLF_REVIEW_VIDEOS =', 1)[1].strip().removesuffix(';'))
    video_links = []
    for entry in video_entries:
        url = entry.get('url', '').strip()
        if not url:
            continue
        if not url.startswith('https://'):
            path = Path(url)
            if path.is_absolute() or '..' in path.parts or path.suffix.lower() != '.mp4' or not (ROOT/path).is_file():
                raise ValueError('La grabación requiere URL HTTPS o ruta MP4 existente: '+url)
            url = 'https://schubertlombeida.github.io/RAG.SALVAGUARDAS.GLF.UEES/'+url
        video_links.append(f"- [{entry['title']}]({url})")
    readme_path = ROOT/'README.md'
    readme = readme_path.read_text(encoding='utf-8')
    block = '<!-- VIDEOS:START -->\n'+('\n'.join(video_links) if video_links else '<!-- Los enlaces públicos se generan desde assets/videos.js. -->')+'\n<!-- VIDEOS:END -->'
    readme = re.sub(r'<!-- VIDEOS:START -->.*?<!-- VIDEOS:END -->', lambda _: block, readme, flags=re.S)
    readme_path.write_text(readme, encoding='utf-8')
    print('index.html: 7 informes, lectura local y navegación estática generadas.')

if __name__ == '__main__':
    build()
