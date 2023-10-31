/*
Perform Z -> mu+mu- skimming.
Runs on a single input file and produces a single output file.
Apart from event selection, branch reduction is performed.
*/

// include c++ library classes 
#include <string>
#include <vector>
#include <algorithm>
#include <exception>
#include <iostream>

// include ROOT classes 
#include "TH1D.h"
#include "TFile.h"
#include "TTree.h"
#include "TROOT.h"
#include "TMath.h"
#include "Math/Vector4D.h"

// definition of constants
const static double ZMass = 91.19;

// definition of b-tag thresholds
// see e.g. subpages of https://twiki.cern.ch/twiki/bin/viewauth/CMS/BtagRecommendation
// the thresholds correspond to loose deep-CSV working point.
double bTagThreshold(const std::string& campaign, const std::string& year){
    if(campaign=="run2preul"){
	if(year=="2016") return 0.2217;
	else if(year=="2017") return 0.1522;
	else if(year=="2018") return 0.1241;
    } else if(campaign=="run2ul"){
	if(year=="2016PreVFP") return 0.2027;
	else if(year=="2016PostVFP") return 0.1918;
        else if(year=="2017") return 0.1355;
        else if(year=="2018") return 0.1208;
    } else{
	std::string msg = "ERROR in bTagThreshold:"; 
        msg += " campaign '" + campaign + "' or year '" + year + "' not recognized.";
        throw std::runtime_error(msg);
    }
    return 0.; // for syntax
}

std::pair<std::string, std::string> getYearFromFileName(const std::string& fileName){
    // small help function to exctract the campaign and year from the name of an input file
    if( fileName.find("RunIISummer20UL16MiniAODAPVv2")!=std::string::npos 
        || fileName.find("HIPM_UL2016_MiniAODv2")!=std::string::npos ){
	return std::make_pair("run2ul", "2016PreVFP"); }
    else if( fileName.find("RunIISummer20UL16MiniAODv2")!=std::string::npos
        || fileName.find("UL2016_MiniAODv2")!=std::string::npos ){
        return std::make_pair("run2ul", "2016PostVFP"); }
    else if( fileName.find("RunIISummer20UL17MiniAODv2")!=std::string::npos
        || fileName.find("UL2017_MiniAODv2")!=std::string::npos ){
        return std::make_pair("run2ul", "2017"); }
    else if( fileName.find("RunIISummer20UL18MiniAODv2")!=std::string::npos
        || fileName.find("UL2018_MiniAODv2")!=std::string::npos ){
        return std::make_pair("run2ul", "2018"); }
    else if( fileName.find("Run2016")!=std::string::npos 
	|| fileName.find("RunIISummer16")!=std::string::npos ){
	return std::make_pair("run2preul", "2016"); }
    else if( fileName.find("Run2017")!=std::string::npos 
	|| fileName.find("RunIIFall17")!=std::string::npos ){
	return std::make_pair("run2preul", "2017"); }
    else if( fileName.find("Run2018")!=std::string::npos 
	|| fileName.find("RunIIAutumn18")!=std::string::npos ){
	return std::make_pair("run2preul", "2018"); }
    else{
	std::string msg = "ERROR: year could not be extracted from filename";
	msg += " " + fileName;
	throw std::runtime_error(msg);
    }
} 

std::vector< std::shared_ptr< TH1 > > getHistogramsFromFile( TFile* f ){
    // get histograms from root file; 
    // note that the file is assumed to be opened and closed outside this function!

    // vector containing all histograms in current file
    std::vector< std::shared_ptr< TH1 > > histogramVector;
    // loop over keys in blackJackAndHookers directory
    TDirectory* dir = (TDirectory*) f->Get("blackJackAndHookers");
    TList* keyList = dir->GetListOfKeys();
    for( const auto objectPtr : *keyList ){
	// try if a dynamic_cast to a histogram works to check if object is histogram
	TH1* histPtr = dynamic_cast< TH1* >( dir->Get( objectPtr->GetName() ) );
	if( histPtr ){
            // make sure histograms don't get deleted by root upon deletion of TDirectory above
            histPtr->SetDirectory( gROOT );
	    histogramVector.emplace_back( histPtr );
	}
    }
    return histogramVector;
}

void skimFile( const std::string& inputFilePath, 
		const std::string& outputFilePath, 
		long unsigned nEntries ){

    std::cout << "skimming " << inputFilePath << std::endl;

    std::pair<std::string, std::string> temp = getYearFromFileName(inputFilePath);
    std::string campaign = temp.first;
    std::string year = temp.second;

    // load input histograms and tree
    TFile* inputFilePtr = TFile::Open( inputFilePath.c_str() );
    std::vector< std::shared_ptr< TH1 > > histVector = getHistogramsFromFile( inputFilePtr );
    TTree* inputTreePtr = (TTree*) inputFilePtr->Get("blackJackAndHookers/blackJackAndHookersTree");
    
    // disable unneeded branches to save disk space
    inputTreePtr->SetBranchStatus("_gen_*",0);
    inputTreePtr->SetBranchStatus("_Flag_*",0);
    inputTreePtr->SetBranchStatus("_HLT_*",0);
    inputTreePtr->SetBranchStatus("_tau*",0);
    inputTreePtr->SetBranchStatus("_ph*",0);
    inputTreePtr->SetBranchStatus("_jet*",0);
    inputTreePtr->SetBranchStatus("_jetEta",1);
    inputTreePtr->SetBranchStatus("_jetPhi",1);
    inputTreePtr->SetBranchStatus("_jetDeepCsv_b",1);
    inputTreePtr->SetBranchStatus("_jetDeepCsv_bb",1);
    inputTreePtr->SetBranchStatus("_met*",0);

    // make output ROOT file
    TFile* outputFilePtr = TFile::Open( outputFilePath.c_str() , "RECREATE" );
    outputFilePtr->mkdir( "blackJackAndHookers" );
    outputFilePtr->cd( "blackJackAndHookers" );

    // write histograms to the new file
    for( const auto& histPtr : histVector ) histPtr->Write();

    // make output tree
    TTree* outputTreePtr = inputTreePtr->CloneTree(0);
    // extend output tree with event variables
    Double_t _nimloth_Mll; outputTreePtr->Branch("_nimloth_Mll",&_nimloth_Mll,"_nimloth_Mll/D");
    UInt_t _nimloth_nJets; outputTreePtr->Branch("_nimloth_nJets",&_nimloth_nJets,"_nimloth_nJets/i");
    // extend output tree with muon variables (always exactly 2 muons per event)
    Double_t _celeborn_lPt[2]; outputTreePtr->Branch("_celeborn_lPt",&_celeborn_lPt,"_celeborn_lPt[2]/D");
    Double_t _celeborn_lEta[2]; outputTreePtr->Branch("_celeborn_lEta",&_celeborn_lEta,"_celeborn_lEta[2]/D");
    Double_t _celeborn_lPhi[2]; outputTreePtr->Branch("_celeborn_lPhi",&_celeborn_lPhi,"_celeborn_lPhi[2]/D");
    UInt_t _celeborn_lCharge[2]; outputTreePtr->Branch("_celeborn_lCharge",&_celeborn_lCharge,"_celeborn_lCharge[2]/I");

    // link input tree branches used to evaluate the skim condition to variables
    // NOTE: nL_max and nJets_max must correspond to the values used in the ntuplizer,
    //       else the skimmer could crash after the event loop with no clear error message... 
    //       would be better to write this as meta-info to the ntuples, 
    //       but not yet done as far as I know.
    //	     for old iteration of the kshort study: nL_max = 20, nJets_max = 20
    //       for new iteration of the kshort study: nL_max = 20, nJets_max = 100
    static const unsigned nL_max = 20;
    static const unsigned nJets_max = 100;
    UInt_t _nL; inputTreePtr->SetBranchAddress("_nL",&_nL);
    UInt_t _nLight; inputTreePtr->SetBranchAddress("_nLight",&_nLight);
    UInt_t _nMu; inputTreePtr->SetBranchAddress("_nMu",&_nMu);
    Bool_t _lPOGMedium[nL_max]; inputTreePtr->SetBranchAddress("_lPOGMedium",_lPOGMedium);
    Double_t _lPt[nL_max]; inputTreePtr->SetBranchAddress("_lPt",_lPt);
    Int_t _lCharge[nL_max]; inputTreePtr->SetBranchAddress("_lCharge",_lCharge);
    Bool_t _passTrigger_mm; inputTreePtr->SetBranchAddress("_passTrigger_mm",&_passTrigger_mm);
    Double_t _lEta[nL_max]; inputTreePtr->SetBranchAddress("_lEta",_lEta);
    Double_t _lPhi[nL_max]; inputTreePtr->SetBranchAddress("_lPhi",_lPhi);
    Double_t _lE[nL_max]; inputTreePtr->SetBranchAddress("_lE",_lE);
    UInt_t _nJets; inputTreePtr->SetBranchAddress("_nJets",&_nJets);
    Double_t _jetPt[nJets_max]; inputTreePtr->SetBranchAddress("_jetPt",_jetPt);
    Double_t _jetEta[nJets_max]; inputTreePtr->SetBranchAddress("_jetEta",_jetEta);
    Double_t _jetPhi[nJets_max]; inputTreePtr->SetBranchAddress("_jetPhi",_jetPhi);
    Double_t _jetDeepCsv_b[nJets_max]; inputTreePtr->SetBranchAddress("_jetDeepCsv_b",_jetDeepCsv_b);
    Double_t _jetDeepCsv_bb[nJets_max]; inputTreePtr->SetBranchAddress("_jetDeepCsv_bb",_jetDeepCsv_bb);

    // start event loop
    unsigned debugcounter = 0;
    if(nEntries<=0) nEntries = inputTreePtr->GetEntries();
    for( long unsigned entry = 0; entry < nEntries; ++entry ){

	inputTreePtr->GetEntry(entry);

        // apply event selection

	// condition: at least two muons
	if(_nMu < 2) continue;

	// make vector of muon indices, useful for indexing (light) lepton arrays further on
	// note: we assume that muons are filled first in the ntuples so indices run from 0 to _nMu
	std::vector<int> muoninds(_nMu);
	for(unsigned i=0; i<_nMu; ++i) muoninds[i] = i;
	
	// condition: the number of muons with lPOGMedium must be exactly 2
	unsigned int i=0;
	while(i<muoninds.size()){
	    if(_lPOGMedium[muoninds[i]]) ++i;
	    else muoninds.erase(muoninds.begin()+i);
	}
	if(muoninds.size()!=2) continue;

	// order by _lPt
	if(_lPt[muoninds[0]]<_lPt[muoninds[1]]) std::swap(muoninds[0],muoninds[1]);

	// condition: explicit momentum and eta cuts
	if(_lPt[muoninds[0]]<30. || _lPt[muoninds[1]]<25.) continue;
	if(std::abs(_lEta[muoninds[0]])>2.4 || std::abs(_lEta[muoninds[1]])>2.4) continue;

	// condition: opposite electric charge
	if(_lCharge[muoninds[0]]*_lCharge[muoninds[1]]>0) continue;

	// set muon variables for output tree
	_celeborn_lPt[0] = _lPt[muoninds[0]]; _celeborn_lPt[1] = _lPt[muoninds[1]];
	_celeborn_lEta[0] = _lEta[muoninds[0]]; _celeborn_lEta[1] = _lEta[muoninds[1]];
	_celeborn_lPhi[0] = _lPhi[muoninds[0]]; _celeborn_lPhi[1] = _lPhi[muoninds[1]];
	_celeborn_lCharge[0] = _lCharge[muoninds[0]]; _celeborn_lCharge[1] = _lCharge[muoninds[1]];

	// condition: pass trigger
	if(!_passTrigger_mm) continue;

	// condition: dimuon invariant mass
	ROOT::Math::PtEtaPhiEVector vec1(_lPt[muoninds[0]],_lEta[muoninds[0]],
				    _lPhi[muoninds[0]],_lE[muoninds[0]]);
	ROOT::Math::PtEtaPhiEVector vec2(_lPt[muoninds[1]],_lEta[muoninds[1]],
				    _lPhi[muoninds[1]],_lE[muoninds[1]]);
	_nimloth_Mll = (vec1+vec2).M();
	if(std::abs(_nimloth_Mll-ZMass)>10.) continue;

	// condition: b-jet veto
	// note: need to reconsider jet from lepton cleaning, maybe to strict here (e.g taus?)!
	// note: also need to consider jet quality cuts,
	//       especially eta requirement for b-tagging score to make sense
	int nbjets = 0;
	_nimloth_nJets = 0;
	for(unsigned j=0; j<_nJets; ++j){
	    // jet pt
	    if( _jetPt[j]<25. ) continue;
	    // remove jets overlapping with leptons
	    bool isleptonjet = false;
	    for(unsigned i=0; i<_nL; ++i){
		double deltaR = std::sqrt( std::pow(_lEta[i]-_jetEta[j],2)
					   +std::pow(_lPhi[i]-_jetPhi[j],2));
		if(deltaR<0.4) {isleptonjet = true; break;}
	    }
	    if(isleptonjet) continue;
	    ++_nimloth_nJets;
	    // check if it is a b-jet
	    double btagvalue = _jetDeepCsv_b[j]+_jetDeepCsv_bb[j];
	    bool inBTagAcceptance = ( std::fabs(_jetEta[j])<2.4 );
	    if( inBTagAcceptance && btagvalue>bTagThreshold(campaign, year) ) ++nbjets;
	}
	if(nbjets>0) continue;

        // fill new tree
	++debugcounter;
        outputTreePtr->Fill();
    }

    // write new tree
    std::cout << "finished event loop, now writing tree" << std::endl;
    outputTreePtr->Write( "",  BIT(2) );

    // close output file
    outputFilePtr->Close();

    // print some results
    std::cout << "skimmed " << inputFilePath <<std::endl;
    std::cout << "processed " << nEntries << " entries, ";
    std::cout << "of which " << debugcounter << " passed the selections" << std::endl;
}


int main( int argc, char* argv[] ){
    std::cerr << "###starting###" << std::endl;
    if( argc != 4 ){
        std::cerr << "### ERROR ###: skimmer requires exactly three arguments to run :" << std::endl;
	std::cerr << "input_file_path, output_file_path, nentries" << std::endl;
        return -1;
    }

    std::vector< std::string > argvStr( &argv[0], &argv[0] + argc );
    std::string& input_file_path = argvStr[1];
    std::string& output_directory = argvStr[2];
    long int nEntries_raw = std::stol(argvStr[3]);
    if(nEntries_raw < 0) nEntries_raw = 0;
    long unsigned nEntries = (long unsigned) nEntries_raw; 
    skimFile( input_file_path, output_directory, nEntries );
    std::cerr << "###done###" << std::endl;
    return 0;
}
