#include <iostream>
#include <fstream>
#include <string>
#include <regex>

#include <ctime>
#include <iomanip>
#include <sstream>

#include <chrono>

using std::chrono::high_resolution_clock;
using std::chrono::duration_cast;
using std::chrono::milliseconds;

// Chunks an extra.xml file into smaller files
//
// Initial development early July 2024
// Tested and confirmed on August 1st 2024
//

/* ----------- COMPILATION INSTRUCTOINS ---------------

Compile:
    - You need to link the pugixml lib
    g++ -std=c++11 chunk_disorder_xml.cpp -o xml_disorder_chunker

Run:
    ./xml_disorder_chunker

 ----------- COMPILATION INSTRUCTOINS --------------- */


// gets a timestamp to append to each file
std::string getCurrentTimestamp() {
    // Get the current time
    std::time_t now = std::time(nullptr);
    std::tm* localTime = std::localtime(&now);

    // Create a string stream to format the time
    std::ostringstream oss;
    //oss << std::put_time(localTime, "%Y%m%d_%H%M");
    oss << std::put_time(localTime, "%Y%m%d");

    // Return the formatted string
    return oss.str();
}

/*
Parses a large xml file of <protein>...</protein> entries and chunks it into smaller 
files, each containing a subset of entries. Each smaller output file is correctly
structured to be a valid xml file in its own right with an appropriate xml header 
and footer. 

To speed up processing, each iteration is passed the line number where the previous 
iteration stopped, allowing the process to relatively quickly find the next 
starting point in the file - there are probably better ways to do this.

*/
int parse_file(int protein_limit, int start_line, int iteration){
    
    // Define the path to the input file
    std::string disorder_file = "/Volumes/My Passport/data/disorder/raw/extra.xml";
    std::string output_folder = "/Volumes/My Passport/data/disorder/split_output/";
    

    // regular expressions to find <protein>...</protein> entities 
    std::regex start_pattern("<protein");
    std::regex end_pattern("protein>");

    // create output filename format
    std::string timestamp = getCurrentTimestamp();
    std::ostringstream oss;
    oss << output_folder << "extras_mobidb_" << timestamp << "_" << iteration << "_.xml";
    std::string output_file = oss.str();

    // timer
    auto start = high_resolution_clock::now();

    // Open the files for reading and writing
    std::ifstream file(disorder_file);
    std::ofstream of(output_file, std::ios::app); // open file to append
    if (!file.is_open()) {
        std::cerr << "Could not open the file!" << std::endl;
        return 1;
    }

    // initialise temp variables
    std::string buffer;
    std::string line;
    std::smatch matches;

    bool match          = false;
    bool limit_reached  = false;
    int protein_count   = 0;
    int line_number     = 0;

    // read each line
    while (std::getline(file, line)) {
        line_number += 1;

        // skip through the file until the last line that was processed
        if ( (start_line > 0) && (line_number <= start_line) ){
            continue;
        }
        // check if the line contains the end of a proetin - ie protein>
        if(std::regex_search(line, matches, end_pattern)){
            //std::cout << "found protein end line " << line << std::endl;
            buffer += line + "\n";
            protein_count +=1;
            match = false;

            // if have reached the max number of proteins to put in a file
            // then ouput the buffer to the file and break from the loop
            if(protein_count >= protein_limit){
                limit_reached = true;
                of << buffer;
                break;
            }
        }
        else if(match){
            //std::cout << "match is true, adding current line " << line << std::endl;
            buffer += line + "\n";
        }
        else if(std::regex_search(line, matches, start_pattern)){
            //std::cout << "found protein start line " << line << std::endl;
            buffer += line + "\n";
            match = true;
        }
        else{
            //std::cout << "Match is false, ignoring line" << line << std::endl;
        }
    }
    // I may have gotten here with some items in the buffer - if so, output the buffer
    if (! limit_reached){
        of << buffer;
        file.close();
        of.close();
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end - start);
        std::cout<< "- reached end of file. protein count: " << protein_count << " time: " << duration.count() << " output: " << output_file << std::endl;
        // return -1 to signify the end
        return -1;
    }
    // if I get here I've reached the limit of proteins for eaach file, return for next iteration
    else{
        file.close();
        of.close();
        auto end = high_resolution_clock::now();
        auto duration = duration_cast<milliseconds>(end - start);
        std::cout<< "- reached protein limit. protein count: " << protein_count << " time: " <<  duration.count() << std::endl;
        // return line number for the next iteration to start from
        return line_number;
    }
}

/*
main method - set the proteins_limit here to signify how many priteins to put in each file

500,000 limit takes about 5min to process on a mac - but it will get slower as it has to prse further into
the ouptut files. 
*/
int main() {
    int proteins_limit  = 500000; // proteins in each chunk, there are 81M protein entries
    int next_start      = 0;
    int iteration       = 0;
    
    std::cout<< getCurrentTimestamp() << " chunking file into sub-chunks of " << proteins_limit << " proteins." << std::endl;

    while(next_start != -1){
        next_start = parse_file(proteins_limit, next_start, iteration);
        iteration +=1;
    }
}
