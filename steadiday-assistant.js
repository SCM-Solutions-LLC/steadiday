/* ============================================================
   STEADIDAY ASSISTANT
   Answers questions about the app by searching a knowledge base
   compiled into this file. There is no backend and no API key:
   steadiday.com is a static site, so a key shipped to the
   browser would be a key anyone could spend. Every answer below
   is lifted from a real page, and every card links to it.

   Scope is deliberately the product only — plans, features,
   accounts, privacy, setup. Health questions get handed to the
   blog and to a doctor rather than answered here.

   To add an answer: add an entry to KB. `keys` carries the words
   people actually type (including misspellings and synonyms);
   `q` is the canonical phrasing shown on the card.
   ============================================================ */

(function () {
    'use strict';

    var SUPPORT = 'support@steadiday.com';

    /* ---------- Knowledge base ---------- */

    var KB = [
        {
            q: 'How much does SteadiDay cost?',
            keys: ['cost', 'price', 'pricing', 'how much', 'expensive', 'fee', 'charge', 'money', 'pay', 'dollar', 'plan', 'subscription', 'free'],
            a: 'The safety essentials are free forever, with no card to enter: Emergency SOS, fall detection, medication reminders (up to 5), task reminders (up to 7), daily check-ins and one trusted contact. Premium is $3.99 a month or $29.99 a year, and there is a $99.99 one-time Lifetime option.',
            link: 'pricing.html',
            linkText: 'Compare all three plans'
        },
        {
            q: 'What do I get with Premium?',
            keys: ['premium', 'paid', 'upgrade', 'unlimited', 'full version', 'whats included', 'features included'],
            a: 'Premium adds unlimited medications and trusted contacts, Family Link caregiver sharing, Apple Health sync, Steady Moves exercises, food and water tracking, calendar sync, Mind Breaks, the helpful tools (magnifier, flashlight, notes, Find My Car), backup and restore, ready-made task ideas, and home screen customisation.',
            link: 'pricing.html',
            linkText: 'See the full feature comparison'
        },
        {
            q: 'Is there a one-time payment option?',
            keys: ['lifetime', 'one time', 'onetime', 'forever', 'single payment', 'buy once', 'no subscription', '99'],
            a: 'Yes. Lifetime is $99.99 paid once and includes every Premium feature plus all future updates, with no monthly or annual fees.',
            link: 'pricing.html',
            linkText: 'See the Lifetime plan'
        },
        {
            q: 'What are the limits on the free plan?',
            keys: ['free plan', 'free limit', 'free tier', 'how many medication', 'how many reminder', 'limit', 'cap', 'maximum'],
            a: 'The free plan covers up to 5 medications, 7 task reminders and 1 trusted contact — enough for most daily routines. Emergency SOS, fall detection, daily check-ins and both Simple and Standard Mode are free with no limit. Premium removes the medication, reminder and contact caps.',
            link: 'pricing.html',
            linkText: 'See what each plan includes'
        },
        {
            q: 'Why are the safety features free?',
            keys: ['why free', 'free forever', 'catch', 'really free', 'how is it free', 'make money'],
            a: 'Everyone deserves access to emergency safety tools regardless of budget, so the SOS button, fall detection, medication reminders and daily check-ins will always be free. Premium features like unlimited medications, Family Link sharing and health tracking fund ongoing development.',
            link: 'index.html#faq',
            linkText: 'Read the FAQ'
        },
        {
            q: 'Does my parent need to create an account?',
            keys: ['account', 'sign up', 'signup', 'register', 'login', 'log in', 'sign in', 'email required'],
            a: 'Not to use the app. They can add medicines, set reminders, use Simple Mode, press SOS to call 911 and call a trusted contact without signing up. A free account switches on the features that reach other people: the automatic alert texts sent when a fall is detected or SOS is pressed, the live-location link, and Family Link. It costs nothing, takes about a minute, and is how we confirm an alert is coming from a real phone and not a stranger.',
            link: 'index.html#faq',
            linkText: 'Read the FAQ'
        },
        {
            q: 'How does Emergency SOS work?',
            keys: ['sos', 'emergency', '911', 'panic button', 'help button', 'call for help', 'emergency button'],
            a: 'Emergency SOS is one tap on the home screen and it is free. Pressing it calls 911, and with a free account your trusted contacts are texted automatically with your location at the same time. One tap also calls a trusted contact directly if that is what is needed instead.',
            link: 'index.html#features',
            linkText: 'See how SOS works'
        },
        {
            q: 'How does fall detection work?',
            keys: ['fall', 'falling', 'fell', 'fall detection', 'falls', 'detect fall', 'tumble', 'alway on', 'always on protection'],
            a: 'Turn on Always-on Protection once and it stays on — there is no session to remember to start. SteadiDay watches for hard falls in the background, and if one is detected with no response within 30 seconds, your trusted contacts are texted automatically with your location. It needs a free SteadiDay account to send those texts and iPhone Location set to Always. If either is missing, the app says protection is limited rather than letting you assume you are covered.',
            link: 'index.html#features',
            linkText: 'See how fall detection works'
        },
        {
            q: 'Do I need a watch or extra device?',
            keys: ['watch', 'apple watch', 'wearable', 'pendant', 'device', 'hardware', 'extra equipment', 'monitor', 'bracelet'],
            a: 'No extra hardware. SteadiDay runs on your parent’s iPhone and uses the phone’s own sensors for fall detection, so there is nothing to charge, wear or replace.',
            link: 'index.html#features',
            linkText: 'See the features'
        },
        {
            q: 'How do medication reminders work?',
            keys: ['medication', 'medicine', 'meds', 'pill', 'prescription', 'dose', 'reminder', 'remind', 'scan label', 'adherence'],
            a: 'Add medications by scanning the label or typing the name, set reminder times, and get gentle notifications. You can track adherence over time and share it with a caregiver through Family Link. Free covers up to 5 medications and 7 reminders; Premium removes both limits.',
            link: 'index.html#features',
            linkText: 'See medication reminders'
        },
        {
            q: 'What is Family Link?',
            keys: ['family link', 'caregiver', 'care summary', 'share', 'sharing', 'adult child', 'son', 'daughter', 'check on', 'monitor parent', 'can i see', 'keep an eye', 'see my mom', 'see my dad', 'see my parent', 'see their medication', 'remotely', 'from my phone'],
            a: 'Family Link shares a private Care Summary with a caregiver: the week’s medication streak, today’s medicines and reminders, the daily check-in and step count at a glance. There is no app to install and no account to set up on the caregiver’s side — it is a simple, private web link that can be turned off at any time. Family Link is a Premium feature.',
            link: 'index.html#features',
            linkText: 'See how Family Link works'
        },
        {
            q: 'What can I see as a trusted contact?',
            keys: ['trusted contact', 'contact', 'alert', 'notified', 'text message', 'who gets told', 'emergency contact'],
            a: 'You are alerted the moment your parent uses the SOS button or a fall is detected. If they choose to share a Care Summary, you also get a daily "everything’s okay" without having to check in. Their day-to-day data stays private unless they decide to share it.',
            link: 'index.html#faq',
            linkText: 'Read the FAQ'
        },
        {
            q: 'What is Simple Mode?',
            keys: ['simple mode', 'simple', 'easy mode', 'large button', 'big button', 'standard mode', 'home screen', 'not tech savvy', 'confusing', 'hard to use'],
            a: 'Simple Mode gives a clean, uncluttered home screen with large buttons for SOS, today’s medicines and reminders, a plain-language line on whether fall protection is on, one tap to call a trusted contact and one to check in. Everything else sits in a simple More menu. Standard Mode instead uses bottom tabs for Home, Reminders, Meds, Health and More. You can switch between them any time in Settings.',
            link: 'index.html#modes',
            linkText: 'Compare the two modes'
        },
        {
            q: 'What if my parent is not good with technology?',
            keys: ['tech savvy', 'technology', 'difficult', 'complicated', 'learn', 'elderly', 'senior', 'old', 'eyesight', 'help them set up'],
            a: 'That is exactly who SteadiDay is built for. Large buttons, clear text and simple navigation mean there is almost nothing to learn — and you can set the whole thing up for them in about five minutes.',
            link: 'index.html#how-it-works',
            linkText: 'See the four setup steps'
        },
        {
            q: 'What are Steady Moves?',
            keys: ['steady moves', 'exercise', 'balance', 'strength', 'workout', 'steadi', 'cdc', 'chair'],
            a: 'Steady Moves are guided daily balance and strength exercises based on CDC STEADI protocols — gentle chair-based routines with voice guidance and large, clear instructions, just a few minutes a day to help prevent falls. It is a Premium feature.',
            link: 'index.html#features',
            linkText: 'See Steady Moves'
        },
        {
            q: 'Does it work with Apple Health?',
            keys: ['apple health', 'healthkit', 'health app', 'steps', 'heart rate', 'sleep', 'sync health'],
            a: 'Yes, with Premium. The health dashboard syncs steps, heart rate, sleep and more from Apple Health. Apple Health data always stays on the device — it is never uploaded.',
            link: 'index.html#features',
            linkText: 'See the health dashboard'
        },
        {
            q: 'Is my parent’s information private?',
            keys: ['privacy', 'private', 'data', 'secure', 'security', 'who can see', 'sell data', 'tracking', 'confidential', 'gdpr', 'hipaa'],
            a: 'Their data is private and secure — stored on their iPhone and protected by its built-in security. If they sign in, some data syncs securely to enable backup and caregiver sharing; Apple Health data always stays on their device. Day-to-day data is never shared with a caregiver unless they choose to share it.',
            link: 'privacy.html',
            linkText: 'Read the privacy policy'
        },
        {
            q: 'How is my data protected?',
            keys: ['encryption', 'encrypted', 'protect', 'breach', 'hack', 'safe', 'server', 'stored where'],
            a: 'The security policy sets out how data is stored and protected, and there is a published data breach policy covering what happens if something goes wrong. Data retention and deletion are covered in their own policy too.',
            link: 'security.html',
            linkText: 'Read the security policy'
        },
        {
            q: 'How do I delete my data?',
            keys: ['delete', 'delete account', 'remove data', 'erase', 'retention', 'how long kept', 'close account'],
            a: 'The data retention policy explains how long each kind of data is kept and how to have it removed. If you want an account and its data deleted, email ' + SUPPORT + ' and the retention policy covers what happens next.',
            link: 'data-retention.html',
            linkText: 'Read the data retention policy'
        },
        {
            q: 'How long does setup take?',
            keys: ['setup', 'set up', 'install', 'get started', 'how long', 'steps', 'begin', 'first time'],
            a: 'About five minutes, in four steps: download the app and pick Simple or Standard Mode; add the people who should be told if something happens and create the free account so SteadiDay can text them; scan a medication label or type the name and choose reminder times; then turn on Always-on Protection and leave it on. No card, nothing to configure.',
            link: 'index.html#how-it-works',
            linkText: 'See the four steps'
        },
        {
            q: 'Where do I download SteadiDay?',
            keys: ['download', 'app store', 'get the app', 'install', 'iphone', 'ios', 'link to app'],
            a: 'SteadiDay is free on the App Store for iPhone. Premium can be added later from inside the app — you do not need to decide at download.',
            link: 'https://apps.apple.com/app/steadiday/id6758526744',
            linkText: 'Get SteadiDay on the App Store'
        },
        {
            q: 'Is there an Android version?',
            keys: ['android', 'samsung', 'google play', 'play store', 'pixel', 'ipad', 'phone support'],
            a: 'SteadiDay is an iPhone app today — it relies on iPhone sensors and Apple Health. There is no Android version available at the moment. Email ' + SUPPORT + ' if you would like to be told when that changes.',
            link: 'index.html',
            linkText: 'See what SteadiDay does'
        },
        {
            q: 'How do I cancel or manage Premium?',
            keys: ['cancel', 'refund', 'unsubscribe', 'stop paying', 'manage subscription', 'billing', 'renew'],
            a: 'Premium is billed through your Apple ID, so it is managed where every iPhone subscription is: Settings → your name → Subscriptions. Cancelling there stops future renewals and the safety essentials keep working for free. Refunds are handled by Apple; the terms of service cover the rest.',
            link: 'terms.html',
            linkText: 'Read the terms of service'
        },
        {
            q: 'What are daily check-ins?',
            keys: ['check in', 'checkin', 'daily check', 'im okay', 'okay button', 'wellness check'],
            a: 'A daily check-in is one tap to say the day is going fine. It is free, it shows up on the Simple Mode home screen, and if a Care Summary is shared the caregiver sees it — so they get an "everything’s okay" without having to phone and ask.',
            link: 'index.html#features',
            linkText: 'See the features'
        },
        {
            q: 'What else is in the app?',
            keys: ['tools', 'magnifier', 'flashlight', 'notes', 'find my car', 'mind break', 'brain game', 'puzzle', 'food', 'water', 'calendar', 'backup', 'restore', 'what else'],
            a: 'Premium adds food and water tracking, Mind Breaks (brain games, word puzzles and calming activities), calendar sync with Apple Reminders, Apple Calendar or Google Calendar, backup and restore so reminders and medicines come back on a new phone, ready-made task ideas, and the helpful tools: magnifier, flashlight, notes and Find My Car.',
            link: 'pricing.html',
            linkText: 'See every feature by plan'
        },
        {
            q: 'Who makes SteadiDay?',
            keys: ['who makes', 'company', 'scm solutions', 'about', 'behind the app', 'where based', 'virginia'],
            a: 'SteadiDay is built by SCM Solutions LLC in Virginia, USA.',
            link: 'index.html',
            linkText: 'About SteadiDay'
        },
        {
            q: 'How do I contact support?',
            keys: ['contact', 'support', 'email', 'help', 'talk to someone', 'customer service', 'phone number', 'reach you'],
            a: 'Email ' + SUPPORT + ' and a real person will reply. That is the right route for billing questions, account deletion, bug reports and anything this assistant could not answer.',
            link: 'mailto:' + SUPPORT,
            linkText: 'Email ' + SUPPORT
        }
    ];

    /* Starter questions. Kept to four so the panel opens without
       a wall of options to read. */
    var STARTERS = [
        'How much does it cost?',
        'How does fall detection work?',
        'Is my data private?',
        'Does my parent need an account?'
    ];

    /* Health questions get handed to a doctor, never answered here.
       The terms come in two strengths, because when they are
       checked matters as much as what they are.

       STRONG terms are clinical: nobody types "dosage" or
       "symptoms" wanting to know about the app. These are checked
       BEFORE the product search, because a product entry can win
       a medical question on a shared word — "what dosage of
       aspirin is safe" matched the security entry on "safe" and
       answered with the data-protection policy. A wrong answer
       there is worse than no answer.

       SOFT terms are health topics that are also ordinary words,
       so they are only consulted once the product search has come
       up empty. That keeps "medication reminders" and "exercises
       for balance" answering as features. */
    var HEALTH_STRONG = [
        'symptom', 'symptoms', 'diagnose', 'diagnosis', 'dosage', 'dose', 'doses',
        'side effect', 'side effects', 'drug interaction', 'interactions', 'milligram', 'mg',
        'prescribe', 'prescribed', 'treatment', 'treat', 'cure', 'should i take',
        'safe to take', 'how much should i take', 'is it bad for', 'contraindication'
    ];

    var HEALTH_SOFT = [
        'disease', 'doctor', 'blood pressure', 'cholesterol', 'diabetes', 'dementia',
        'alzheimer', 'arthritis', 'cancer', 'vitamin', 'supplement', 'diet', 'nutrition',
        'vaccine', 'flu', 'covid', 'pain', 'hurt', 'ache', 'dizzy', 'sleep apnea',
        'weight loss', 'stroke', 'heart attack', 'kidney', 'osteoporosis', 'fracture',
        'depression', 'anxiety', 'infection', 'blood test', 'cognitive decline'
    ];

    var STOPWORDS = {
        a: 1, an: 1, and: 1, are: 1, as: 1, at: 1, be: 1, but: 1, by: 1, can: 1, do: 1,
        does: 1, for: 1, from: 1, get: 1, has: 1, have: 1, how: 1, i: 1, if: 1, in: 1,
        is: 1, it: 1, its: 1, me: 1, my: 1, of: 1, on: 1, or: 1, that: 1, the: 1, there: 1,
        this: 1, to: 1, up: 1, was: 1, what: 1, when: 1, where: 1, which: 1, will: 1,
        with: 1, you: 1, your: 1
    };

    /* ---------- Search ---------- */

    function normalise(text) {
        return String(text).toLowerCase().replace(/[^a-z0-9\s]/g, ' ').replace(/\s+/g, ' ').trim();
    }

    /* Enough stemming to tie "falls"/"falling"/"fell" to "fall"
       without pulling in a stemmer library. */
    function stem(word) {
        if (word.length > 5 && /ing$/.test(word)) return word.slice(0, -3);
        if (word.length > 4 && /ed$/.test(word)) return word.slice(0, -2);
        if (word.length > 4 && /ies$/.test(word)) return word.slice(0, -3) + 'y';
        if (word.length > 3 && /es$/.test(word)) return word.slice(0, -2);
        if (word.length > 3 && /s$/.test(word)) return word.slice(0, -1);
        return word;
    }

    function tokenise(text) {
        var words = normalise(text).split(' ');
        var out = [];
        for (var i = 0; i < words.length; i++) {
            var w = words[i];
            if (!w || STOPWORDS[w]) continue;
            out.push(stem(w));
        }
        return out;
    }

    /* Each entry gets its searchable text stemmed once, up front,
       so a keystroke-fast search never re-does the work.

       Single-word keys and the words inside multi-word keys are
       indexed apart, because conflating them ranks badly: every
       word of "how many medication" scored as a full keyword hit,
       which let the plan-limits entry tie with the medication
       entry on the query "medication reminders". A word borrowed
       from a phrase is a weak signal; the phrase itself is a
       strong one. */
    for (var i = 0; i < KB.length; i++) {
        var single = [];
        var fromPhrase = [];
        var phrases = [];
        for (var k = 0; k < KB[i].keys.length; k++) {
            var key = KB[i].keys[k];
            var words = tokenise(key);
            if (key.indexOf(' ') > -1) {
                phrases.push(normalise(key));
                fromPhrase = fromPhrase.concat(words);
            } else {
                single = single.concat(words);
            }
        }
        KB[i]._keys = ' ' + single.join(' ') + ' ';
        KB[i]._phraseWords = ' ' + fromPhrase.join(' ') + ' ';
        KB[i]._phrases = phrases;
        KB[i]._q = ' ' + tokenise(KB[i].q).join(' ') + ' ';
        KB[i]._a = ' ' + tokenise(KB[i].a).join(' ') + ' ';
    }

    function search(query) {
        var raw = normalise(query);
        var tokens = tokenise(query);
        if (!tokens.length) return [];

        var scored = [];
        for (var i = 0; i < KB.length; i++) {
            var entry = KB[i];
            var score = 0;

            /* A typed phrase that matches a key outright is the
               strongest signal there is — "how much" beating a
               scatter of single-word hits elsewhere. */
            for (var k = 0; k < entry._phrases.length; k++) {
                if (raw.indexOf(entry._phrases[k]) > -1) score += 10;
            }

            for (var t = 0; t < tokens.length; t++) {
                var tok = ' ' + tokens[t] + ' ';
                if (entry._keys.indexOf(tok) > -1) score += 6;
                else if (entry._q.indexOf(tok) > -1) score += 3;
                else if (entry._phraseWords.indexOf(tok) > -1) score += 2;
                else if (entry._a.indexOf(tok) > -1) score += 1;
            }

            if (score > 0) scored.push({ entry: entry, score: score / tokens.length });
        }

        scored.sort(function (a, b) { return b.score - a.score; });

        /* Only keep runners-up that are genuinely close to the
           best match, so a confident answer is not buried under
           three weak ones. */
        var out = [];
        for (var s = 0; s < scored.length && out.length < 3; s++) {
            if (scored[s].score < 1.5) continue;
            if (out.length && scored[s].score < scored[0].score * 0.55) break;
            out.push(scored[s].entry);
        }
        return out;
    }

    function matchesAny(query, terms) {
        var raw = normalise(query);
        var padded = ' ' + raw + ' ';
        for (var i = 0; i < terms.length; i++) {
            var term = normalise(terms[i]);
            if (term.indexOf(' ') > -1) {
                if (raw.indexOf(term) > -1) return true;
            } else if (padded.indexOf(' ' + term + ' ') > -1) {
                return true;
            }
        }
        return false;
    }

    /* ---------- Links ---------- */

    /* Knowledge base links are written as if from the site root.
       Blog posts live one level down, so they need the hop. */
    var BASE = /\/blog\//.test(window.location.pathname) ? '../' : '';

    function resolve(href) {
        if (/^(https?:|mailto:)/.test(href)) return href;
        return BASE + href;
    }

    /* ---------- Rendering ---------- */

    var panel, body, input, launcher, liveRegion, lastFocus;

    function el(tag, className, text) {
        var node = document.createElement(tag);
        if (className) node.className = className;
        if (text != null) node.textContent = text;
        return node;
    }

    function resultCard(entry) {
        var card = el('div', 'sd-assistant-result');
        card.appendChild(el('h3', null, entry.q));
        card.appendChild(el('p', null, entry.a));
        var a = el('a', null, entry.linkText);
        a.href = resolve(entry.link);
        card.appendChild(a);
        return card;
    }

    function noticeCard(heading, parts) {
        var card = el('div', 'sd-assistant-notice');
        card.appendChild(el('h3', null, heading));
        var p = el('p');
        for (var i = 0; i < parts.length; i++) {
            if (typeof parts[i] === 'string') {
                p.appendChild(document.createTextNode(parts[i]));
            } else {
                var a = el('a', null, parts[i].text);
                a.href = resolve(parts[i].href);
                p.appendChild(a);
            }
        }
        card.appendChild(p);
        return card;
    }

    /* `shown` are the entries already on screen. Offering
       "How much does it cost?" directly underneath the answer to
       that very question reads like the assistant was not
       listening, so those starters are dropped. */
    function starterList(heading, shown) {
        var skip = (shown || []).map(function (entry) { return entry.q; });
        var offer = STARTERS.filter(function (question) {
            var top = search(question)[0];
            return !top || skip.indexOf(top.q) === -1;
        });
        if (!offer.length) return null;

        var wrap = el('div');
        wrap.appendChild(el('p', 'sd-assistant-intro', heading));
        var list = el('ul', 'sd-assistant-chips');
        offer.forEach(function (question) {
            var li = el('li');
            var chip = el('button', 'sd-assistant-chip', question);
            chip.type = 'button';
            chip.addEventListener('click', function () {
                input.value = question;
                answer(question);
            });
            li.appendChild(chip);
            list.appendChild(li);
        });
        wrap.appendChild(list);
        return wrap;
    }

    function showWelcome() {
        body.textContent = '';
        var starters = starterList('Popular questions');
        if (starters) body.appendChild(starters);
    }

    function announce(message) {
        /* Cleared first so a repeated message is still read out. */
        liveRegion.textContent = '';
        window.setTimeout(function () { liveRegion.textContent = message; }, 60);
    }

    function answer(query) {
        /* A clinical question is routed before the search runs, so
           no product card can win it on a shared word. */
        var clinical = matchesAny(query, HEALTH_STRONG);
        var matches = clinical ? [] : search(query);
        body.textContent = '';

        var asked = el('p', 'sd-assistant-asked');
        asked.appendChild(document.createTextNode('You asked: '));
        asked.appendChild(el('strong', null, query));
        body.appendChild(asked);

        if (matches.length) {
            matches.forEach(function (entry) { body.appendChild(resultCard(entry)); });
            announce(matches.length === 1
                ? 'One answer found: ' + matches[0].q
                : matches.length + ' answers found. ' + matches[0].q);
        } else if (clinical || matchesAny(query, HEALTH_SOFT)) {
            body.appendChild(noticeCard('That one is for your doctor', [
                'This assistant only answers questions about the SteadiDay app, so it is the wrong place for health advice — please talk to a doctor or pharmacist about anything medical. Our ',
                { href: 'blog/index.html', text: 'health blog' },
                ' covers topics like this with sources, and it is worth reading alongside professional advice rather than instead of it.'
            ]));
            announce('This assistant answers questions about the app only. Health questions are better for a doctor.');
        } else {
            body.appendChild(noticeCard('No answer for that one', [
                'Nothing in here matched that. Try asking about pricing, the free plan, Emergency SOS, fall detection, medication reminders, Family Link, Simple Mode, privacy or setup — or email ',
                { href: 'mailto:' + SUPPORT, text: SUPPORT },
                ' and a real person will reply.'
            ]));
            announce('No answer found for that question.');
        }

        var starters = starterList(matches.length ? 'Also asked' : 'Try one of these', matches);
        if (starters) {
            var more = el('div', 'sd-assistant-more');
            more.appendChild(starters);
            body.appendChild(more);
        }
        body.scrollTop = 0;

        if (typeof window.gtag === 'function') {
            window.gtag('event', 'assistant_query', {
                search_term: query,
                results: matches.length
            });
        }
    }

    /* ---------- Panel wiring ---------- */

    var ICON_ASK = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';
    var ICON_CLOSE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M18 6 6 18M6 6l12 12"/></svg>';
    var ICON_SEND = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>';

    function open() {
        lastFocus = document.activeElement;
        panel.hidden = false;
        launcher.hidden = true;
        launcher.setAttribute('aria-expanded', 'true');
        input.focus();
    }

    function close() {
        panel.hidden = true;
        launcher.hidden = false;
        launcher.setAttribute('aria-expanded', 'false');
        if (lastFocus && typeof lastFocus.focus === 'function') lastFocus.focus();
        else launcher.focus();
    }

    /* Tab stays inside the panel while it is open, so a keyboard
       user cannot wander into the page behind it. */
    function trapTab(event) {
        if (event.key !== 'Tab') return;
        var stops = panel.querySelectorAll('button, input, a[href]');
        if (!stops.length) return;
        var first = stops[0];
        var last = stops[stops.length - 1];
        if (event.shiftKey && document.activeElement === first) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    }

    function build() {
        launcher = el('button', 'sd-assistant-launcher');
        launcher.type = 'button';
        launcher.id = 'sd-assistant-launcher';
        launcher.setAttribute('aria-expanded', 'false');
        launcher.setAttribute('aria-controls', 'sd-assistant-panel');
        launcher.innerHTML = ICON_ASK;
        launcher.appendChild(document.createTextNode('Ask a question'));
        launcher.addEventListener('click', open);

        panel = el('div', 'sd-assistant-panel');
        panel.id = 'sd-assistant-panel';
        panel.hidden = true;
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-modal', 'false');
        panel.setAttribute('aria-labelledby', 'sd-assistant-heading');

        var head = el('div', 'sd-assistant-head');
        var title = el('div', 'sd-assistant-title');
        var heading = el('h2', null, 'Ask about SteadiDay');
        heading.id = 'sd-assistant-heading';
        title.appendChild(heading);
        title.appendChild(el('p', null, 'Questions about plans, features, privacy and setup — answered from this site.'));
        head.appendChild(title);

        var closeBtn = el('button', 'sd-assistant-close');
        closeBtn.type = 'button';
        closeBtn.innerHTML = ICON_CLOSE;
        closeBtn.setAttribute('aria-label', 'Close the question panel');
        closeBtn.addEventListener('click', close);
        head.appendChild(closeBtn);
        panel.appendChild(head);

        var form = el('form', 'sd-assistant-form');
        form.setAttribute('role', 'search');
        input = el('input', 'sd-assistant-input');
        input.type = 'search';
        input.id = 'sd-assistant-input';
        input.placeholder = 'Type your question';
        input.setAttribute('aria-label', 'Type your question about SteadiDay');
        input.autocomplete = 'off';
        form.appendChild(input);

        var send = el('button', 'sd-assistant-send');
        send.type = 'submit';
        send.innerHTML = ICON_SEND;
        send.setAttribute('aria-label', 'Find an answer');
        form.appendChild(send);

        form.addEventListener('submit', function (event) {
            event.preventDefault();
            var query = input.value.trim();
            if (query) answer(query);
        });
        panel.appendChild(form);

        body = el('div', 'sd-assistant-body');
        body.id = 'sd-assistant-results';
        panel.appendChild(body);

        liveRegion = el('p', 'sd-assistant-live');
        liveRegion.setAttribute('aria-live', 'polite');
        panel.appendChild(liveRegion);

        panel.addEventListener('keydown', trapTab);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && !panel.hidden) close();
        });

        document.body.appendChild(launcher);
        document.body.appendChild(panel);
        showWelcome();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', build);
    } else {
        build();
    }
})();
