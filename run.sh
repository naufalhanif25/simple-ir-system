#!/bin/bash
read -ra raw_name <<< "$(ls ./*.py 2>/dev/null)"

conf_path="sh_config.conf"
file_name="${raw_name[*]}"
file_name="${file_name:2}"

update_config() {
    local key=$1
    local value=$2
    local config_file=$3

    if grep -q "^$key=" "$config_file"; then
        sed -i "s/^$key=.*/$key=$value/" "$config_file"
    else
        echo "$key=$value" >> "$config_file"
    fi
}

echo_help() {
    echo -e "Using: ./run.sh [COMMAND] [FILE]\n"

    echo "Commands:"
    echo "  start   : Run the information retrieval system program [Ex: ./run.sh start]"
    echo "  to-html : Convert ipynb file to html [Ex: ./run.sh to-html preprocessing.ipynb]"
    echo "  help    : Show help message [Ex: ./run.sh help]"
    echo "  version : Show version [Ex: ./run.sh version]"
}

command -v poetry >/dev/null 2>&1
is_poetry_exists=$?

command -v python >/dev/null 2>&1
is_python_exists=$?

source "$conf_path"

if [[ "$1" == "start" ]]; then
    if [[ is_poetry_exists -eq 0 && is_python_exists -eq 0 ]]; then
        if [[ $file_name != "" ]]; then
            if [[ $POETRY_DEP_INSTALLED == false ]]; then
                poetry install --no-root
                poetry run python "$file_name"
                update_config "POETRY_DEP_INSTALLED" true "$conf_path"
            else
                poetry run python "$file_name"
            fi
        else
            echo "Error: No such file or directory"
            exit 1
        fi

        exit 0
    elif [[ is_poetry_exists -eq 1 && is_python_exists -eq 0 ]]; then
        echo "Warning: 'poetry' command is not recognized"

        if [[ $file_name != "" ]]; then
            python "$file_name"
        else
            echo "Error: No such file or directory"
            exit 1
        fi

        exit 0
    else
        echo "Error: 'python' command is not recognized"
        exit 127
    fi
elif [[ "$1" == "to-html" ]]; then
    jupyter nbconvert --to html "$2"
elif [[ "$1" == "help" ]]; then
    echo_help
elif [[ "$1" == "version" ]]; then
    echo "$PROGRAM_NAME $PROGRAM_VERSION"
else
    echo_help
fi