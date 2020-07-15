#!/bin/bash

COMMAND=$(echo $SSH_ORIGINAL_COMMAND | awk '{print $1}' )
PARAM1=$(echo $SSH_ORIGINAL_COMMAND | awk '{print $2}' )

case "$COMMAND" in
'WOL')
        echo "WOL $PARAM1"
        my_wakeonlan $PARAM1
        ;;
*)
        echo "ERROR '$COMMAND'"
        ;;
esac

