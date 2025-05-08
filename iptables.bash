#!/usr/bin/bash 
# Load the environment with all our tailored settings
. .env
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Get the NIC
nic_name=$( ip -o -4 addr show | awk '{print $2" "$4}' | grep $HOST_IP_FOR_DICOM | awk '{print $1}' )
if [[ ${nic_name} ]]; then

   echo "Found NIC: $nic_name"

   option="0"
   while [ "$option" -ne 100 ]
   do

      #clear

      # ----------------------------------------------------------
      # Look for existing rules for AET ports
      # ----------------------------------------------------------
      declare -A port_addresses
      declare -A port_open
      declare -A port_iprange
      ip_line_min=0
      for ip_address_range in $( iptables -S INPUT | grep $nic_name | awk '{print $4}' | sort -u ); do
         ip_address=$( echo $ip_address_range | awk '{split($0,a,"/"); print a[1]}' )
         ip_line=$( iptables -L INPUT -n -v --line-number | grep $nic_name | grep $ip_address | head -1 | awk '{print $1}' )
         ip_ports=()
         for ip_port in $( iptables -L INPUT -n -v --line-number | grep $nic_name | grep $ip_address | grep "dpt" | awk '{split($NF,a,":"); print a[2]}' ); do
            if [[ ${ip_ports} ]]; then
               ip_ports="$ip_ports,$ip_port"
            else
               ip_ports="$ip_port"
            fi
         done
         if [[ $ip_ports =~ $PHI_DICOM_PORT ]]; then
            port_open+=([$ip_address]="OPEN")
         else
            port_open+=([$ip_address]="CLOSED")
         fi
         ip_line=${ip_line[0]}
         if [ $ip_line -gt $ip_line_min ]; then
            ip_line_min=$ip_line
         fi
         port_addresses+=([$ip_address]=$ip_ports)
         port_iprange+=([$ip_address]=$ip_address_range)
      done

      # ----------------------------------------------------------
      # Check whether HTTP port is locked
      # ----------------------------------------------------------
      nic_anon_locked=$( iptables -S OUTPUT | grep $ANON_NIC | grep 48 )
      nic_phi_locked=$( iptables -S OUTPUT | grep $PHI_NIC | grep 48 )
      
      # ----------------------------------------------------------
      # Present options
      # ----------------------------------------------------------
      option_number=0
      declare -A option_to_ip_address
      printf "Options:\n\n"
      for ip_address in "${!port_addresses[@]}"; do
         if [ "${port_open[$ip_address]}" == "443" ]; then
            continue
         fi
         option_number=$((option_number+1))
         option_to_ip_address+=([$option_number]=$ip_address)
         if [ ${port_open[$ip_address]} == "OPEN" ]; then
            printf "   %3d) PHI ${CYAN}DICOM${NC} port %d is ${GREEN}%6s${NC} on network ${YELLOW}%15s${NC} where open ports are:${GREEN}%s${NC}\n" $option_number $PHI_DICOM_PORT "OPEN" $ip_address ${port_addresses[$ip_address]}
            IFSOLD=$IFS
            IFS=$'\n'
            for line_of_text in $( iptables -S INPUT | grep $nic_name | grep $ip_address | grep $PHI_DICOM_PORT ); do 
               printf "       %s\n" "$line_of_text"
            done
            IFS=$IFSOLD
            #line_of_text=$( iptables -L INPUT -n -v --line-number | grep $nic_name | grep $ip_address | grep $PHI_DICOM_PORT | head -1 )
            #printf "         Current iptables INPUT: %s\n" "$line_of_text"
         else
            printf "   %3d) PHI ${CYAN}DICOM${NC} port %d is ${RED}%6s${NC} on network ${YELLOW}%15s${NC} where open ports are:${GREEN}%s${NC}\n" $option_number $PHI_DICOM_PORT "CLOSED" $ip_address ${port_addresses[$ip_address]}
         fi
      done
      if [ "$nic_anon_locked" == "" ]; then
         printf "    97) Port access to Anon web is ${RED}NOT Locked${NC} (Locking recommended)\n"
      else
         printf "    97) Port access to Anon web is ${GREEN}Locked${NC} (This is good!)\n"
      fi
      if [ "$nic_phi_locked" == "" ]; then
         printf "    98) Port access to Phi web is ${RED}NOT Locked${NC} (Locking recommended)\n"
      else
         printf "    98) Port access to Phi web is ${GREEN}Locked${NC} (This is good!)\n"
      fi
      printf "    99) Reconcile iptables DOCKER\n"  
      IFSOLD=$IFS
      IFS=$'\n'
      for line_of_text in $( iptables -S DOCKER | grep $PHI_DICOM_PORT ); do 
         printf "       %s\n" "$line_of_text"
      done
      IFS=$IFSOLD
      printf "   100) Quit\n\n"
      printf "Enter option to toggle or 100 to quit: "
      read option

      if [ "$option" == "" ]; then
         option=0
      fi

      # ----------------------------------------------------------
      # Evaluate options
      # ----------------------------------------------------------
      # Toggling AET ports
      if [ "$option" -gt 0 -a "$option" -lt 97 ]; then
         ip_address=${option_to_ip_address[$option]}
         if [ ${port_open[$ip_address]} == "OPEN" ]; then
            ip_line=$( iptables -L INPUT -n -v --line-number | grep $nic_name | grep $ip_address | grep $PHI_DICOM_PORT | head -1 | awk '{print $1}' )
            printf "\nRemoving: iptables -D INPUT %d\n" $ip_line
            iptables -D INPUT $ip_line
         else
            printf "\nAdding: iptables -A INPUT -s %s -i %s -p tcp -m tcp --dport %d -j ACCEPT\n" ${port_iprange[$ip_address]} $nic_name $PHI_DICOM_PORT
            iptables -A INPUT -s ${port_iprange[$ip_address]} -i $nic_name -p tcp -m tcp --dport $PHI_DICOM_PORT -j ACCEPT
         fi
      fi
      if [ "$option" == 97 ]; then
         if [ "$nic_anon_locked" == "" ]; then
            printf "   Locking Port access to Anon web\n"
            ip_drop_line=$( iptables -L OUTPUT -n -v --line-number | grep 8042 | grep DROP | head -1 | awk '{print $1}' )
            ip_line=$((ip_drop_line-1))
            iptables -I OUTPUT $ip_line -o $ANON_NIC -p tcp -m tcp --dport 8042 -m owner --uid-owner 48 -j ACCEPT
         else
            printf "   Unlocking Port access to Anon web\n"
            ip_line=$( iptables -L OUTPUT -n -v --line-number | grep $ANON_NIC | grep 48 | head -1 | awk '{print $1}' )
            iptables -D OUTPUT $ip_line
         fi
      fi
      if [ "$option" == 98 ]; then
         if [ "$nic_phi_locked" == "" ]; then
            printf "   Locking Port access to Phi web\n"
            ip_drop_line=$( iptables -L OUTPUT -n -v --line-number | grep 8042 | grep DROP | head -1 | awk '{print $1}' )
            ip_line=$((ip_drop_line-1))
            iptables -I OUTPUT $ip_line -o $PHI_NIC -p tcp -m tcp --dport 8042 -m owner --uid-owner 48 -j ACCEPT
         else
            printf "   Unlocking Port access to Phi web\n"
            ip_line=$( iptables -L OUTPUT -n -v --line-number | grep $PHI_NIC | grep 48 | head -1 | awk '{print $1}' )
            iptables -D OUTPUT $ip_line
         fi
      fi
      if [ "$option" == 99 ]; then
         ip_drop_line=$( iptables -L DOCKER -n -v --line-number | grep $nic_name | grep $PHI_DICOM_PORT | grep DROP | head -1 | awk '{print $1}' )
         if [ "$ip_drop_line" == "" ]; then
            iptables -I DOCKER -i $nic_name -p tcp -m tcp --dport $PHI_DICOM_PORT -j DROP 
         else
            iptables -D DOCKER $ip_drop_line
         fi
         for ip_drop_line in $( iptables -L DOCKER -n -v --line-number | grep $PHI_DICOM_PORT | grep -v $PHI_NIC | grep ACCEPT | awk '{print $1}' ); do 
            iptables -D DOCKER $ip_drop_line
         done
         for ip_address in "${!port_addresses[@]}"; do
            if [ "${port_open[$ip_address]}" == "443" ]; then
               continue
            fi
            if [ ${port_open[$ip_address]} == "OPEN" ]; then
               iptables -I DOCKER -s ${port_iprange[$ip_address]} -i $nic_name -p tcp -m tcp --dport $PHI_DICOM_PORT -j ACCEPT
            fi
         done
         iptables -S DOCKER
         sleep 3
      fi

      if [ "$option" -lt 100 ]; then
         sleep 2
      fi

      unset port_addresses
      unset port_open
      unset port_iprange
      unset option_to_ip_address
      
   done

else

   echo "No nic associated with IP: $HOST_IP_FOR_DICOM"

fi
 
