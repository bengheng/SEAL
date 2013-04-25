clear
reset
unset key
set term pos eps color enhanced "Times-Roman" defaultplex 24
set title "Histogram of Email Delays"
set output "./histogram.eps"

set xlabel "Email Delays (secs)"
set ylabel "Frequency"

set xtics rotate out
set xtics 0,10000
set style data histogram
set style fill solid border
everyfifth(col) = (int(column(col)) % 25 == 0) ? stringcolumn(1) : ""
plot "combined_out.csv" using 2:xticlabels(everyfifth(0)) title 'test'
