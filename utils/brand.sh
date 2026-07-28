#!/usr/bin/env bash
# SPDX-License-Identifier: AGPL-3.0-or-later

# shellcheck source=utils/lib.sh
. /dev/null

build.env.export() {
    GIT_BRANCH="$(git branch | grep '\*' | cut -d' ' -f2-)"
    GIT_REMOTE="$(git config "branch.${GIT_BRANCH}.remote")"
    GIT_URL="$(git config --get "remote.${GIT_REMOTE}.url")"
    if [[ "${GIT_URL}" == git@* ]]; then
        GIT_URL="${GIT_URL/://}"
        GIT_URL="${GIT_URL/git@/https://}"
    fi
    if [[ "${GIT_URL}" == *.git ]]; then
        GIT_URL="${GIT_URL%.git}"
    fi

    aperion_URL="$(python "${REPO_ROOT}/utils/get_setting.py" server.base_url)"
    aperion_PORT="$(python "${REPO_ROOT}/utils/get_setting.py" server.port)"
    aperion_BIND_ADDRESS="$(python "${REPO_ROOT}/utils/get_setting.py" server.bind_address)"
    export GIT_URL
    export GIT_BRANCH
    export aperion_URL
    export aperion_PORT
    export aperion_BIND_ADDRESS

}

pushd "${REPO_ROOT}" &>/dev/null
build.env.export
popd &>/dev/null
