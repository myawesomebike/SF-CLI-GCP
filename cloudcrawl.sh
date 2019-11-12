#!/usr/bin/bash

echo "Enter domain to crawl"

read domain

screamingfrogseospider --crawl $domain --headless --output-folder ~/crawl-data/ \
--export-tabs "Internal:All,Directives:All" --overwrite --bulk-export "All Inlinks"

now=$(date +"%Y_%m_%d")
filename=${domain//./_}
filename=${filename//[:\/-]/}
filename=${filename:0:53}
filename=$filename$now

tr '\0' ' ' < ~/crawl-data/internal_all.csv > ~/crawl-data/internal_all_clean.csv
tr '\0' ' ' < ~/crawl-data/directives_all.csv > ~/crawl-data/directives_all_clean.csv
tr '\0' ' ' < ~/crawl-data/all_inlinks.csv > ~/crawl-data/all_inlinks_clean.csv

bq load --autodetect --source_format=CSV --allow_quoted_newlines --allow_jagged_rows --ignore_unknown_values \
screaming_frog_crawls.${filename}_internal ~/crawl-data/internal_all_clean.csv

bq load --autodetect --source_format=CSV --allow_quoted_newlines --allow_jagged_rows --ignore_unknown_values \
screaming_frog_crawls.${filename}_directives ~/crawl-data/directives_all_clean.csv

bq load --autodetect --source_format=CSV --allow_quoted_newlines --allow_jagged_rows --ignore_unknown_values \
screaming_frog_crawls.${filename}_inlinks ~/crawl-data/all_inlinks_clean.csv

curl -i -H "Content-Type:application/json; charset=UTF-8" --data '{"text":"'"$domain"' crawl complete"}' "https://chat.googleapis.com/{token}"
