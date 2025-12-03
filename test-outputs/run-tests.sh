#!/bin/bash
rm -f /home/mike/fixrepo/savebirchanger/test-outputs/responses2.txt

for i in {1..20}; do
  case $((i % 5)) in
    0) answers='["Lived here 30 years, raised my family here","Prevents villages merging, protects ancient woodland","Traffic gridlock every morning","Schools full, had to appeal for my child","No bus on Sundays, station too far to walk"]' ;;
    1) answers='["Just moved here last year","Green Belt keeps villages separate","Worried about more cars","GP waiting times are 3 weeks","Car dependent, no safe cycling routes"]' ;;
    2) answers='["Work in the area, commute through daily","Historic church setting would be ruined","Infrastructure cannot cope","Forest Hall oversubscribed","2km to station with no footpath"]' ;;
    3) answers='["Retired here 15 years ago for peace and quiet","Openness and countryside views","Developer promises never delivered","No sixth form locally","Bus 308 unreliable and infrequent"]' ;;
    4) answers='["Family has lived here for generations","Wildlife corridor, see deer and foxes regularly","Who pays for school buildings?","Already long waits for everything","Completely car dependent location"]' ;;
  esac

  echo "=== Test $i ===" >> /home/mike/fixrepo/savebirchanger/test-outputs/responses2.txt
  curl -s -X POST https://template-generator.martinssolver.workers.dev \
    -H "Content-Type: application/json" \
    -d "{\"templateType\":\"planning-objection\",\"answers\":$answers}" | jq -r '.content' >> /home/mike/fixrepo/savebirchanger/test-outputs/responses2.txt
  echo -e "\n\n" >> /home/mike/fixrepo/savebirchanger/test-outputs/responses2.txt
  sleep 2
  echo "Completed test $i"
done

echo "Done - 20 tests completed"
