#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later

data.help() {
    cat <<EOF
data.:
  all       : update aperion/sxng_locales.py and aperion/data/*
  traits    : update aperion/data/engine_traits.json & aperion/sxng_locales.py
  useragents: update aperion/data/useragents.json with the most recent versions of Firefox
  locales   : update aperion/data/locales.json from babel
  currencies: update aperion/data/currencies.json from wikidata
EOF
}

data.all() {
    (
        set -e

        pyenv.activate
        data.traits
        data.useragents
        data.locales

        build_msg DATA "update aperion/data/osm_keys_tags.json"
        pyenv.cmd python aperion_extra/update/update_osm_keys_tags.py
        build_msg DATA "update aperion/data/ahmia_blacklist.txt"
        python aperion_extra/update/update_ahmia_blacklist.py
        build_msg DATA "update aperion/data/wikidata_units.json"
        python aperion_extra/update/update_wikidata_units.py
        build_msg DATA "update aperion/data/currencies.json"
        python aperion_extra/update/update_currencies.py
        build_msg DATA "update aperion/data/external_bangs.json"
        python aperion_extra/update/update_external_bangs.py
        build_msg DATA "update aperion/data/engine_descriptions.json"
        python aperion_extra/update/update_engine_descriptions.py
    )
}

data.traits() {
    (
        set -e
        pyenv.activate
        build_msg DATA "update aperion/data/engine_traits.json"
        python aperion_extra/update/update_engine_traits.py
        build_msg ENGINES "update aperion/sxng_locales.py"
    )
    dump_return $?
}

data.useragents() {
    build_msg DATA "update aperion/data/useragents.json"
    pyenv.cmd python aperion_extra/update/update_firefox_version.py
    dump_return $?
}

data.locales() {
    (
        set -e
        pyenv.activate
        build_msg DATA "update aperion/data/locales.json"
        python aperion_extra/update/update_locales.py
    )
    dump_return $?
}

data.currencies() {
    (
        set -e
        pyenv.activate
        build_msg DATA "update aperion/data/currencies.json"
        python aperion_extra/update/update_currencies.py
    )
    dump_return $?
}
