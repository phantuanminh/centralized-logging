free -m |tail -2|awk '{ printf("%-8s||  %-8s|||\n",$2, $3); }' | head -n 20 
grep 'cpu ' /proc/stat | awk '{usage=($2+$4)*100/($2+$4+$5)} END {print usage "%"}'
