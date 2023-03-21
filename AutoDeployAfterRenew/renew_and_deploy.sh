echo "received $#"
echo "targets : $@"
echo "----------------"

path="/etc/letsencrypt/live"

in_array() {
    local needle array value
    needle="$1"
    shift
    array=("${@}")
    for value in ${array[@]}
      do
        if [[ "$value" == "$needle" ]]
        then
          echo "true"
          return
        fi
      done
    echo "false"
}

lines=$(sudo certbot renew –dry-run | grep "(success)")
for line in $lines
do
  z=$(echo $line | cut -c 23- | tr "/" "\n")
  for x in $z
  do
    if [[ "$x" =~ "fullchain.pem" ]]
    then
      :
    else
      if [ $# -ne 0 ]
      then
        array_check=`in_array "$x" "$@"`
        if [ "${array_check}" == "true" ]; then
          echo "sh $path/$x/deploy.sh"
          break
        fi
      else
        echo $x
      fi
    fi
  done
done