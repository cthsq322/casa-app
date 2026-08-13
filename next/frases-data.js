/* ── FRASES DE CAMPO ─────────────────────────────────────────
   Single source of truth for all field phrase templates.
   Used by:
     • frases.html — reference page, renders sections s1-s3, s6-s7 from here
     • index.html  — picker when tapping "✍ текст агенту"
   Edit here → both pages update automatically.
─────────────────────────────────────────────────────────────── */

// Concelhos where fire-risk question shows first in the picker
window.FRASES_FIRE_CONCELHOS = [
  'Pedrógão Grande', 'Castanheira de Pêra', 'Figueiró dos Vinhos',
  'Alvaiázere', 'Ansião', 'Sertã', 'Góis', 'Pampilhosa da Serra'
];

// The 5 picker templates, in default display order.
// Fire-risk reordering (show incendio first) happens in index.html JS.
//
// pt_raw:     plain-text body used by the picker (null → built dynamically).
// pt_display: version shown in frases.html (uses [X] placeholders → rendered as <em>).
//             null means pt_raw is used as display text.
// note_ru:    fill instructions shown under the phrase card in frases.html.
window.FRASES_PICKER = [
  {
    id: 'primeiro-contacto',
    label: '1 · Primeiro contacto',
    stepId: 's1',
    stepNum: '1',
    title: 'Primeiro contacto — estilo de rota',
    why_ru: 'Час привязан к маршруту, не к желанию. Снимает торг о дне. Сразу спрашивает про кредит.',
    dynamic: true,   // text built by buildFirstContact(h) in index.html
    fireRisk: false,
    pt_raw: null,
    pt_display: 'Bom dia.\nReferência: [TIPO, CIDADE] — [portal] [número].\n\nEstamos a fazer uma rota pela zona, com os dias já montados — por isso as horas estão presas ao caminho, não à nossa vontade.\n\nEsta casa fica-nos a jeito [QUANDO]. Dá-lhe jeito?\n\nSe essa hora não servir, diga qual serve nesse mesmo dia — é mais fácil trocar a hora do que o dia.\n\nNestes dias queremos ver o máximo possível para fechar uma lista curta. Se a casa nos agradar, voltamos numa segunda visita com calma e com família.\n\nSe tiver mais casas nesta zona — mesmo as que ainda não estão no site — mande os links.\n\nAntes de avançarmos: a casa passa no crédito e está pronta para a avaliação do banco? Temos aprovação de dois bancos e vamos à avaliação, por isso conseguimos fechar depressa.\n\nCumprimentos,\nSerhii',
    note_ru: 'Preenchido automaticamente: tipo, cidade, portal, número, hora. Tocar no app → copia + abre WhatsApp.'
  },
  {
    id: 'docs-banco',
    label: '2 · Docs e banco',
    stepId: 's2',
    stepNum: '2',
    title: 'Bloco de perguntas — documentos e banco',
    why_ru: 'Сегодня отсёк два дома без единого километра. Слать ВСЕГДА перед визитом.',
    dynamic: false,
    fireRisk: false,
    pt_raw: 'Antes de agendarmos, algumas questões importantes:\n\n• O imóvel é elegível para financiamento bancário?\n• Tem licença de utilização válida?\n• A caderneta predial e a certidão do registo estão atualizadas?\n• Tem certificado energético? Qual é a classe?\n• As plantas correspondem ao que está construído — sem obras por legalizar?\n• Prevê algum problema para passar na avaliação bancária?\n\nPerguntamos porque temos crédito aprovado e queremos avançar rápido — se houver alguma restrição preferimos saber já, e agradecemos a franqueza.',
    pt_display: null,
    note_ru: 'Отсекает дома с проблемами ДО поездки. Обязательно перед каждым визитом.'
  },
  {
    id: 'incendio',
    label: '3 · Zona de incêndio',
    stepId: 's3',
    stepNum: '3',
    title: 'Zona de risco de incêndio',
    why_ru: 'После пожаров 2017 банки отказывают по объектам в ZRI. Добавлять к блоку 2 для этих муниципий.',
    dynamic: false,
    fireRisk: true,
    pt_raw: 'Uma questão adicional: o imóvel encontra-se em zona de risco de incêndio? Existe alguma restrição documental que impeça o financiamento bancário?\n\nPerguntamos porque noutra casa desta região nos disseram que havia restrições ligadas a essa classificação.',
    pt_display: null,
    note_ru: 'Прямо спросить про ZRI. Можно добавить к блоку выше одним сообщением.'
  },
  {
    id: 'mudar-hora',
    label: '4 · Mudar hora',
    stepId: 's6',
    stepNum: '6',
    title: 'Mudar a hora da visita',
    why_ru: 'Apareceu outro objeto — o percurso deslocou-se.',
    dynamic: false,
    fireRisk: false,
    pt_raw: 'Surgiu uma visita em [CIDADE] às [HORA] que não conseguimos remarcar. Seria possível passar a nossa visita de [DIA] das [HORA] para as [NOVA HORA]?\n\nConfirmamos presença — continuamos muito interessados. Obrigado pela compreensão.',
    pt_display: null,
    note_ru: 'Заменить: [CIDADE] нового объекта, его [HORA], [DIA], старый час, [NOVA HORA].'
  },
  {
    id: 'cancelar',
    label: '5 · Cancelar → reagendar',
    stepId: 's7',
    stepNum: '7',
    title: 'Cancelar com reagendamento',
    why_ru: 'Не приехали — не молчать. Один message сохраняет отношения.',
    dynamic: false,
    fireRisk: false,
    pt_raw: 'Peço desculpa pelo incómodo — hoje não conseguimos chegar a tempo.\n\nGostaríamos de manter o interesse na casa: seria possível reagendar para [DIA] de manhã? Obrigado pela compreensão.',
    pt_display: null,
    note_ru: 'Заменить [DIA]. Утро — потому что чаще соглашаются.'
  }
];
