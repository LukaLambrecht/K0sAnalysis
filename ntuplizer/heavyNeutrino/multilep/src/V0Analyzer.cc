/*
Custom analyzer class for finding secondary vertices corresponding to Light Neutral Hadron (V0) decays.
*/

// include header
// note: all other includes are defined in the header
#include "heavyNeutrino/multilep/interface/V0Analyzer.h"

// constructor //
V0Analyzer::V0Analyzer(const edm::ParameterSet& iConfig, multilep* multilepAnalyzer):
    multilepAnalyzer(multilepAnalyzer){
};

// destructor //
V0Analyzer::~V0Analyzer(){
}

// beginJob //
void V0Analyzer::beginJob(TTree* outputTree){
    // initialize branches in the output tree

    // beamspot position
    outputTree->Branch("_beamSpotX", &_beamSpotX, "_beamSpotX/D");
    outputTree->Branch("_beamSpotY", &_beamSpotY, "_beamSpotY/D");
    outputTree->Branch("_beamSpotZ", &_beamSpotZ, "_beamSpotZ/D");
    // primary vertex position and position uncertainty
    outputTree->Branch("_primaryVertexX", &_primaryVertexX, "_primaryVertexX/D");
    outputTree->Branch("_primaryVertexY", &_primaryVertexY, "_primaryVertexY/D");
    outputTree->Branch("_primaryVertexZ", &_primaryVertexZ, "_primaryVertexZ/D");
    outputTree->Branch("_primaryVertexXUnc", &_primaryVertexXUnc, "_primaryVertexXUnc/D");
    outputTree->Branch("_primaryVertexYUnc", &_primaryVertexYUnc, "_primaryVertexYUnc/D");
    outputTree->Branch("_primaryVertexZUnc", &_primaryVertexZUnc, "_primaryVertexZUnc/D");
    // V0 compound variables
    // - ID variables
    outputTree->Branch("_nV0s", &_nV0s, "_nV0s/i");
    outputTree->Branch("_V0InvMass", &_V0InvMass, "_V0InvMass[_nV0s]/D");
    outputTree->Branch("_V0Type", &_V0Type, "_V0Type[_nV0s]/i");
    // - vertex position and position uncertainty
    outputTree->Branch("_V0X", &_V0X, "_V0X[_nV0s]/D");
    outputTree->Branch("_V0Y", &_V0Y, "_V0Y[_nV0s]/D");
    outputTree->Branch("_V0Z", &_V0Z, "_V0Z[_nV0s]/D");
    outputTree->Branch("_V0XUnc", &_V0XUnc, "_V0XUnc[_nV0s]/D");
    outputTree->Branch("_V0YUnc", &_V0YUnc, "_V0YUnc[_nV0s]/D");
    outputTree->Branch("_V0ZUnc", &_V0ZUnc, "_V0ZUnc[_nV0s]/D");
    // - radial distance, uncertainty and significance
    outputTree->Branch("_V0RPV", &_V0RPV, "_V0RPV[_nV0s]/D");
    outputTree->Branch("_V0RBS", &_V0RBS, "_V0RBS[_nV0s]/D");
    outputTree->Branch("_V0RPVUnc", &_V0RPVUnc, "_V0RPVUnc[_nV0s]/D");
    outputTree->Branch("_V0RBSUnc", &_V0RBSUnc, "_V0RBSUnc[_nV0s]/D");
    outputTree->Branch("_V0RPVSig", &_V0RPVSig, "_V0RPVSig[_nV0s]/D");
    outputTree->Branch("_V0RBSSig", &_V0RBSSig, "_V0RBSSig[_nV0s]/D");
    // - momentum and direction
    outputTree->Branch("_V0Px", &_V0Px, "_V0Px[_nV0s]/D");
    outputTree->Branch("_V0Py", &_V0Py, "_V0Py[_nV0s]/D");
    outputTree->Branch("_V0Pz", &_V0Pz, "_V0Pz[_nV0s]/D");
    outputTree->Branch("_V0Pt", &_V0Pt, "_V0Pt[_nV0s]/D");
    outputTree->Branch("_V0Eta", &_V0Eta, "_V0Eta[_nV0s]/D");
    outputTree->Branch("_V0Phi", &_V0Phi, "_V0Phi[_nV0s]/D");
    // - point of closest approach
    outputTree->Branch("_V0DCA", &_V0DCA, "_V0DCA[_nV0s]/D");
    outputTree->Branch("_V0PCAX", &_V0PCAX, "_V0PCAX[_nV0s]/D");
    outputTree->Branch("_V0PCAY", &_V0PCAY, "_V0PCAY[_nV0s]/D");
    outputTree->Branch("_V0PCAZ", &_V0PCAZ, "_V0PCAZ[_nV0s]/D");
    // - other
    outputTree->Branch("_V0VtxNormChi2", &_V0VtxNormChi2, "_V0VtxNormChi2[_nV0s]/D");
    // V0 decay track variables
    // - momentum and direction
    outputTree->Branch("_V0PxPos", &_V0PxPos, "_V0PxPos[_nV0s]/D");
    outputTree->Branch("_V0PyPos", &_V0PyPos, "_V0PyPos[_nV0s]/D");
    outputTree->Branch("_V0PzPos", &_V0PzPos, "_V0PzPos[_nV0s]/D");
    outputTree->Branch("_V0PtPos", &_V0PtPos, "_V0PtPos[_nV0s]/D");
    outputTree->Branch("_V0PxNeg", &_V0PxNeg, "_V0PxNeg[_nV0s]/D");
    outputTree->Branch("_V0PyNeg", &_V0PyNeg, "_V0PyNeg[_nV0s]/D");
    outputTree->Branch("_V0PzNeg", &_V0PzNeg, "_V0PzNeg[_nV0s]/D");
    outputTree->Branch("_V0PtNeg", &_V0PtNeg, "_V0PtNeg[_nV0s]/D");
    outputTree->Branch("_V0EtaPos", &_V0EtaPos, "_V0EtaPos[_nV0s]/D");
    outputTree->Branch("_V0EtaNeg", &_V0EtaNeg, "_V0EtaNeg[_nV0s]/D");
    outputTree->Branch("_V0PhiPos", &_V0PhiPos, "_V0PhiPos[_nV0s]/D");
    outputTree->Branch("_V0PhiNeg", &_V0PhiNeg, "_V0PhiNeg[_nV0s]/D");
    // - track quality variables
    outputTree->Branch("_V0NHitsPos", &_V0NHitsPos, "_V0NHitsPos[_nV0s]/D");
    outputTree->Branch("_V0NHitsNeg", &_V0NHitsNeg, "_V0NHitsNeg[_nV0s]/D");
    outputTree->Branch("_V0NormChi2Pos", &_V0NormChi2Pos, "_V0NormChi2Pos[_nV0s]/D");
    outputTree->Branch("_V0NormChi2Neg", &_V0NormChi2Neg, "_V0NormChi2Neg[_nV0s]/D");
    outputTree->Branch("_V0D0Pos", &_V0D0Pos, "_V0D0Pos[_nV0s]/D");
    outputTree->Branch("_V0DzPos", &_V0DzPos, "_V0DzPos[_nV0s]/D");
    outputTree->Branch("_V0D0Neg", &_V0D0Neg, "_V0D0Neg[_nV0s]/D");
    outputTree->Branch("_V0DzNeg", &_V0DzNeg, "_V0DzNeg[_nV0s]/D");
    outputTree->Branch("_V0IsoPos", &_V0IsoPos, "_V0IsoPos[_nV0s]/D");
    outputTree->Branch("_V0IsoNeg", &_V0IsoNeg, "_V0IsoNeg[_nV0s]/D");
}

// analyze (main method) //
void V0Analyzer::analyze(const edm::Event& iEvent, const reco::Vertex& primaryVertex){
    edm::Handle<std::vector<pat::Electron>> electrons;
    iEvent.getByToken(multilepAnalyzer->eleToken, electrons);
    edm::Handle<std::vector<pat::Muon>> muons;
    iEvent.getByToken(multilepAnalyzer->muonToken, muons);
    edm::Handle<std::vector<pat::PackedCandidate>> packedCandidates;
    iEvent.getByToken(multilepAnalyzer->packedCandidatesToken, packedCandidates);
    edm::Handle<std::vector<pat::PackedCandidate>> lostTracks;
    iEvent.getByToken(multilepAnalyzer->lostTracksToken, lostTracks);
    edm::Handle<reco::BeamSpot> beamSpotHandle;
    iEvent.getByToken(multilepAnalyzer->beamSpotToken, beamSpotHandle);
    MagneticField* bfield = new OAEParametrizedMagneticField("3_8T");

    // store primary vertex position and position uncertainty
    _primaryVertexX = primaryVertex.position().x();
    _primaryVertexY = primaryVertex.position().y();
    _primaryVertexZ = primaryVertex.position().z();
    _primaryVertexXUnc = primaryVertex.xError();
    _primaryVertexYUnc = primaryVertex.yError();
    _primaryVertexZUnc = primaryVertex.zError();

    // store beamspot position
    _beamSpotX = beamSpotHandle->position().x();
    _beamSpotY = beamSpotHandle->position().y();
    _beamSpotZ = beamSpotHandle->position().z();

    // preselect PackedCandidates and lost tracks (see help function below)
    std::vector<reco::Track> seltracks;
    for(const pat::PackedCandidate pc: *packedCandidates){
	if(pc.hasTrackDetails()){
	    reco::Track tr;
	    tr = *pc.bestTrack();
            std::unordered_map<std::string, double> temp = getTrackVariables(tr,beamSpotHandle,bfield);
	    if(temp["pass"]>0.5) seltracks.push_back(tr);
        }
    }
    for(const pat::PackedCandidate pc : *lostTracks){
	if(pc.hasTrackDetails()){
	    reco::Track tr;
	    tr = *pc.bestTrack();
	    std::unordered_map<std::string, double> temp = getTrackVariables(tr,beamSpotHandle,bfield);
	    if(temp["pass"]>0.5) seltracks.push_back(tr);
	}
    }

    // initialize number of V0s
    _nV0s = 0;

    // loop over pairs of tracks
    for(unsigned i=0; i<seltracks.size(); i++){
        for(unsigned j=i+1; j<seltracks.size(); j++){
            const reco::Track tr1 = seltracks.at(i);
            const reco::Track tr2 = seltracks.at(j);
	    // temporary try catch for 2018D files giving a strange 
	    // "BasicSingleVertexState::could not invert weight matrix" error
	    // that presumably has something to do with the kalman fitter
	    std::unordered_map<std::string, double> temp;
	    try{
		// combine pair of tracks into a V0 vertex
		// (see help function below)
		temp = VZeroFitter(tr1, tr2, beamSpotHandle, primaryVertex, bfield, iEvent);
	    } catch(...){ continue; }

	    // if no valid type was found, continue without writing a new V0 candidate
	    if(temp.at("type")<0.5) continue;

	    // write V0 properties
	    _V0InvMass[_nV0s] = temp.at("invmass");
	    _V0Type[_nV0s] = temp.at("type");
	    _V0X[_nV0s] = temp.at("vtxx");
	    _V0Y[_nV0s] = temp.at("vtxy");
	    _V0Z[_nV0s] = temp.at("vtxz");
	    _V0XUnc[_nV0s] = temp.at("vtxxunc");
            _V0YUnc[_nV0s] = temp.at("vtxyunc");
            _V0ZUnc[_nV0s] = temp.at("vtxzunc");
	    _V0RPV[_nV0s] = temp.at("vtxr_pv");
	    _V0RBS[_nV0s] = temp.at("vtxr_bs");
	    _V0RPVUnc[_nV0s] = temp.at("vtxrunc_pv");
            _V0RBSUnc[_nV0s] = temp.at("vtxrunc_bs");
	    _V0RPVSig[_nV0s] = temp.at("vtxrsig_pv");
            _V0RBSSig[_nV0s] = temp.at("vtxrsig_bs");
	    _V0Px[_nV0s] = temp.at("px");
            _V0Py[_nV0s] = temp.at("py");
            _V0Pz[_nV0s] = temp.at("pz");
            _V0Pt[_nV0s] = temp.at("pt");
	    _V0Eta[_nV0s] = temp.at("eta");
	    _V0Phi[_nV0s] = temp.at("phi");
	    _V0DCA[_nV0s] = temp.at("dca");
	    _V0PCAX[_nV0s] = temp.at("pcax");
	    _V0PCAY[_nV0s] = temp.at("pcay");
	    _V0PCAZ[_nV0s] = temp.at("pcaz");
	    _V0VtxNormChi2[_nV0s] = temp.at("vtxnormchi2");
	    _V0PxPos[_nV0s] = temp.at("pxpos");
	    _V0PyPos[_nV0s] = temp.at("pypos");
	    _V0PzPos[_nV0s] = temp.at("pzpos");
	    _V0PtPos[_nV0s] = temp.at("ptpos");
	    _V0PxNeg[_nV0s] = temp.at("pxneg");
	    _V0PyNeg[_nV0s] = temp.at("pyneg");
	    _V0PzNeg[_nV0s] = temp.at("pzneg");
	    _V0PtNeg[_nV0s] = temp.at("ptneg");
	    _V0EtaPos[_nV0s] = temp.at("etapos");
            _V0EtaNeg[_nV0s] = temp.at("etaneg");
	    _V0PhiPos[_nV0s] = temp.at("phipos");
	    _V0PhiNeg[_nV0s] = temp.at("phineg");
	    _V0NHitsPos[_nV0s] = temp.at("nhitspos");
	    _V0NHitsNeg[_nV0s] = temp.at("nhitsneg");
	    _V0NormChi2Pos[_nV0s] = temp.at("normchi2pos");
	    _V0NormChi2Neg[_nV0s] = temp.at("normchi2neg");
	    _V0D0Pos[_nV0s] = temp.at("d0pos");
	    _V0DzPos[_nV0s] = temp.at("dzpos");
	    _V0D0Neg[_nV0s] = temp.at("d0neg");
	    _V0DzNeg[_nV0s] = temp.at("dzneg");
	    _V0IsoPos[_nV0s] = temp.at("isopos");
	    _V0IsoNeg[_nV0s] = temp.at("isoneg");

	    ++_nV0s; 
            if(_nV0s == nV0s_max) break;
        }
        if(_nV0s == nV0s_max) break;
    }
    delete bfield;
}


std::unordered_map<std::string, double> V0Analyzer::getTrackVariables(
	const reco::Track& tr,
	edm::Handle<reco::BeamSpot> beamSpotHandle,
	MagneticField* bfield){
    // get properties of an individual track
    // (and do preliminary selection)

    std::unordered_map<std::string, double> outputmap = {
	{"loosequality",0.}, 
	{"transip",0.},
	{"pass",0.} // combined flag for final selection
    };
    // set variables and apply minimal selection
    outputmap["loosequality"] = (tr.quality(reco::TrackBase::qualityByName("loose")))? 1.: 0.;
    if(outputmap["loosequality"] < 0.5) return outputmap;
    // special for impact parameter: use proper extrapolation to beamspot
    FreeTrajectoryState initialFTS = trajectoryStateTransform::initialFreeState(tr, bfield);
    TSCBLBuilderNoMaterial blsBuilder;
    TrajectoryStateClosestToBeamLine tscb(blsBuilder(initialFTS, *beamSpotHandle));
    if(!tscb.isValid()){ outputmap["pass"] = 0.; return outputmap; }
    outputmap["transip"] = tscb.transverseImpactParameter().significance();
    if(outputmap["transip"] < 2.) return outputmap;
    // selections are passed; put flag pass to true and return the map
    outputmap["pass"] = 1.;
    return outputmap;
}


double V0Analyzer::getTrackRelIso(const reco::Track& tr, const edm::Event& iEvent){
    // calculate relative isolation of a track
    // (still to check if this works correctly or if there isn't a better way)
    // (however, not yet used in further analysis, so harmless for now)
    edm::Handle<std::vector<pat::PackedCandidate>> packedCandidates;
    iEvent.getByToken(multilepAnalyzer->packedCandidatesToken, packedCandidates);
    edm::Handle<std::vector<pat::PackedCandidate>> lostTracks;
    iEvent.getByToken(multilepAnalyzer->lostTracksToken, lostTracks);
    double relIso = 0;
    for(const pat::PackedCandidate pc: *packedCandidates){
	double dR = reco::deltaR(tr,pc);
	if(dR<0.3 and dR>1e-10){
	    relIso = relIso + pc.pt();
	}
    }
    for(const pat::PackedCandidate pc : *lostTracks){
	double dR = reco::deltaR(tr,pc);
	if(dR<0.3 and dR>1e-10){
	    relIso = relIso + pc.pt();
	}
    }
    relIso = relIso/tr.pt();
    return relIso;
}


reco::Track fixTrackCovariance(const reco::Track& tk, double delta=1e-6){
  // see here: https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackingPOGRecommendations
  unsigned int i, j;
  // Initialize minimum eigenvalue to a default value.
  double min_eig = 1;
  // Get the original covariance matrix.
  reco::TrackBase::CovarianceMatrix cov = tk.covariance();
  // Convert it from an SMatrix to a TMatrixD so we can get the eigenvalues.
  TMatrixDSym new_cov(cov.kRows);
  for (i = 0; i < cov.kRows; i++) {
    for (j = 0; j < cov.kRows; j++) {
      // Need to check for nan or inf, because for some reason these cause a segfault when calling Eigenvectors()
      if (std::isnan(cov(i,j)) || std::isinf(cov(i,j))) cov(i,j) = 1e-6;
      // In all other cases, just copy the values over from cov to new_cov.
      new_cov(i,j) = cov(i,j);
    }
  }
  // Get the eigenvalues.
  TVectorD eig(cov.kRows);
  new_cov.EigenVectors(eig);
  // Find the minimum eigenvalue
  for (i = 0; i < cov.kRows; i++){
    if (eig(i) < min_eig){
      min_eig = eig(i);
    }
  }
  // If the minimum eigenvalue is less than zero, then subtract it from the diagonal and add `delta`.
  if (min_eig < 0) {
    for (i = 0; i < cov.kRows; i++){
      cov(i,i) -= min_eig - delta;
    }
  } 
  return reco::Track(tk.chi2(), tk.ndof(), tk.referencePoint(), 
                     tk.momentum(), tk.charge(), cov, tk.algo(), 
                     (reco::TrackBase::TrackQuality) tk.qualityMask()); 
}


std::unordered_map<std::string, double> V0Analyzer::VZeroFitter(const reco::Track& tr1, 
						const reco::Track& tr2,
						edm::Handle<reco::BeamSpot> beamSpotHandle,
						const reco::Vertex& primaryVertex,
						MagneticField* bfield,
						const edm::Event& iEvent){
    // FIT AND SELECT V0 VERTICES FROM TWO TRACKS AND CALCULATE PROPERTIES
    std::unordered_map<std::string, double> outputmap = { 
	    {"type",-1.},{"invmass",0.},
	    {"vtxx",0.}, {"vtxy",0.}, {"vtxz",0.},
	    {"vtxxunc",0.}, {"vtxyunc",0.}, {"vtxzunc",0.},
	    {"vtxr_pv",0.}, {"vtxr_bs",0.},
	    {"vtxrunc_pv",0.}, {"vtxrunc_bs",0.},
	    {"vtxrsig_pv",0.}, {"vtxrsig_bs",0.},
	    {"px",0.}, {"py",0.}, {"pz",0.}, {"pt",0.},
	    {"eta",0.},{"phi",0.},
	    {"dca",0.}, {"pcax",0.}, {"pcay",0.}, {"pcaz",0.}, 
	    {"vtxnormchi2",0.},
	    {"pxpos",0.}, {"pypos",0.}, {"pzpos",0.}, {"ptpos",0.}, 
	    {"pxneg",0.}, {"pyneg",0.}, {"pzneg",0.}, {"ptneg",0.}, 
	    {"etapos",0.}, {"etaneg",0.},
	    {"phipos",0.}, {"phineg",0.},
	    {"nhitspos",0.}, {"nhitsneg",0.},
	    {"normchi2pos",0.}, {"normchi2neg",0.},
	    {"d0pos",0.}, {"dzpos",0.}, {"d0neg",0.}, {"dzneg",0.},
	    {"isopos",0.}, {"isoneg",0.}
    };
    
    // candidates must have opposite charge
    if(tr1.charge()*tr2.charge()>0) return outputmap;
    
    // the following fragment applies some conditions on the point of closest approach,
    // namely that the distance of closest approach must be reasonably small
    // and that the point of closest approach must be situated not too far from the center of CMS.
    reco::TransientTrack trtr1(tr1, bfield);
    reco::TransientTrack trtr2(tr2, bfield);
    if(!trtr1.impactPointTSCP().isValid() or !trtr2.impactPointTSCP().isValid()) return outputmap;
    FreeTrajectoryState state1 = trtr1.impactPointTSCP().theState();
    FreeTrajectoryState state2 = trtr2.impactPointTSCP().theState();
    ClosestApproachInRPhi capp; capp.calculate(state1,state2);
    if(!capp.status()) return outputmap;
    double dca = fabs(capp.distance());
    outputmap["dca"] = dca;
    GlobalPoint cxpt = capp.crossingPoint();
    if(dca < 0. or dca > 1.) return outputmap;
    if(std::sqrt(cxpt.x()*cxpt.x() + cxpt.y()*cxpt.y())>120.
        or std::abs(cxpt.z())>300.) return outputmap;
    outputmap["pcax"] = cxpt.x();
    outputmap["pcay"] = cxpt.y();
    outputmap["pcaz"] = cxpt.z();

    // the following fragment calculates the trajectory states at PCA and applies preliminary cut on mass
    // (assuming pion masses for both tracks)
    // note: this cut has now been disabled as it is a little vague,
    //       it is for example not clear what the bias is for tracks that are not from pions.
    TrajectoryStateClosestToPoint tscp1 = 
	trtr1.trajectoryStateClosestToPoint( cxpt );
    TrajectoryStateClosestToPoint tscp2 =
	trtr2.trajectoryStateClosestToPoint( cxpt );
    if(!tscp1.isValid() or !tscp2.isValid()) return outputmap;
    /*double totalE = sqrt(tscp1.momentum().mag2() + pimass2) +
	              sqrt( tscp2.momentum().mag2() + pimass2);
    double totalESq = totalE*totalE;
    double totalPSq = (tscp1.momentum() + tscp2.momentum() ).mag2();
    double mass = sqrt(totalESq - totalPSq);
    if(mass > 0.6) return outputmap; // default: 0.6 */

    // preliminary conditions are met; now fit a vertex and perform further selections
    // note: need to apply the fix for track covariance matrices recommended here:
    //       https://twiki.cern.ch/twiki/bin/viewauth/CMS/TrackingPOGRecommendations
    reco::Track tr1fix = fixTrackCovariance(tr1);
    reco::Track tr2fix = fixTrackCovariance(tr2);
    std::vector<reco::TransientTrack> transtracks;
    transtracks.push_back(reco::TransientTrack(tr1fix, bfield));
    transtracks.push_back(reco::TransientTrack(tr2fix, bfield));
    KalmanVertexFitter vtxFitter(true); // use option true to include track refitting!
    TransientVertex v0vtx = vtxFitter.vertex(transtracks);
    // condition: vertex must be valid
    if(!v0vtx.isValid()) return outputmap;
    // condition: chi squared of fit must be small
    if(v0vtx.normalisedChiSquared()>15.) return outputmap;
    if(v0vtx.normalisedChiSquared()<0.) return outputmap;
    outputmap["vtxnormchi2"] = v0vtx.normalisedChiSquared();
    // calculate refitted tracks for further selection
    std::vector<reco::TransientTrack> refittedTracks;
    if(v0vtx.hasRefittedTracks()) refittedTracks = v0vtx.refittedTracks();
    else return outputmap; // should not happen when using option true in vtxFitter

    // convert TransientVertex to RecoVertex for later use
    reco::Vertex v0recovtx = v0vtx;
    // store vertex position to output map
    outputmap["vtxx"] = v0recovtx.position().x();
    outputmap["vtxy"] = v0recovtx.position().y();
    outputmap["vtxz"] = v0recovtx.position().z();
    outputmap["vtxxunc"] = v0recovtx.xError();
    outputmap["vtxyunc"] = v0recovtx.yError();
    outputmap["vtxzunc"] = v0recovtx.zError();
    // convert vertex, beamspot and primary vertex position to GlobalPoints for later use
    GlobalPoint vtxXYZ(v0vtx.position().x(), v0vtx.position().y(), v0vtx.position().z());
    GlobalPoint beamSpotXYZ(beamSpotHandle->position().x(),
			      beamSpotHandle->position().y(),
			      beamSpotHandle->position().z());
    GlobalPoint primaryVertexXYZ(primaryVertex.position().x(),
    				primaryVertex.position().y(),
    				primaryVertex.position().z());

    // calculate transverse displacement (+ unc and sig) with respect to the beamspot
    ROOT::Math::SVector<double, 3> vtxrvec_bs(vtxXYZ.x()-beamSpotXYZ.x(), 
						vtxXYZ.y()-beamSpotXYZ.y(), 0.);
    double vtxr_bs = ROOT::Math::Mag(vtxrvec_bs);
    ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3>> totalcovmat_bs = 
			beamSpotHandle->rotatedCovariance3D() + v0recovtx.covariance();
    double vtxrunc_bs = sqrt(ROOT::Math::Similarity(totalcovmat_bs, vtxrvec_bs))/vtxr_bs;
    double vtxrsig_bs = vtxr_bs/vtxrunc_bs;
    outputmap["vtxr_bs"] = vtxr_bs;
    outputmap["vtxrunc_bs"] = vtxrunc_bs;
    outputmap["vtxrsig_bs"] = vtxrsig_bs;
    // calculate transverse displacement (+ unc and sig) with respect to primary vertex
    ROOT::Math::SVector<double, 3> vtxrvec_pv(vtxXYZ.x()-primaryVertexXYZ.x(), 
						vtxXYZ.y()-primaryVertexXYZ.y(), 0.);
    double vtxr_pv = ROOT::Math::Mag(vtxrvec_pv);
    ROOT::Math::SMatrix<double, 3, 3, ROOT::Math::MatRepSym<double, 3>> totalcovmat_pv = 
			primaryVertex.covariance() + v0recovtx.covariance();
    double vtxrunc_pv = sqrt(ROOT::Math::Similarity(totalcovmat_pv, vtxrvec_pv))/vtxr_pv;
    double vtxrsig_pv = vtxr_pv/vtxrunc_pv;
    outputmap["vtxr_pv"] = vtxr_pv;
    outputmap["vtxrunc_pv"] = vtxrunc_pv;
    outputmap["vtxrsig_pv"] = vtxrsig_pv;

    // apply cut on inner hit position with respect to vertex position (ONLY IN RECO!)
    /*if(tr1.innerOk()){
        reco::Vertex::Point inpos1 = tr1.innerPosition();
        double inpos1d0 = sqrt(pow(inpos1.x()-beamSpotPos.x(),2) + pow(inpos1.y()-beamSpotPos.y(),2));
	if(inpos1d0 < vtxd0-4*vtxd0sigma) return outputmap; // default: 4
    }
    if(tr2.innerOk()){
        reco::Vertex::Point inpos2 = tr2.innerPosition();
        double inpos2d0 = sqrt(pow(inpos2.x()-beamSpotPos.x(),2) + pow(inpos2.y()-beamSpotPos.y(),2));
	if(inpos2d0 < vtxd0-4*vtxd0sigma) return outputmap; // default: 4
    }*/

    // calculate properties of tracks at the vertex
    reco::Track postrack;
    reco::Track negtrack;
    reco::TransientTrack posrefittedtranstrack;
    reco::TransientTrack negrefittedtranstrack;
    if(tr1.charge()>0. and tr2.charge()<0){
        postrack = tr1;
        negtrack = tr2;
	posrefittedtranstrack = refittedTracks.at(0);
	negrefittedtranstrack = refittedTracks.at(1);
    } else if(tr1.charge()<0. and tr2.charge()>0){
	postrack = tr2;
	negtrack = tr1;
	posrefittedtranstrack = refittedTracks.at(1);
        negrefittedtranstrack = refittedTracks.at(0);
    } else return outputmap; // should not normally happen but just for safety
    TrajectoryStateClosestToPoint postscp = 
	posrefittedtranstrack.trajectoryStateClosestToPoint(vtxXYZ);
    TrajectoryStateClosestToPoint negtscp = 
	negrefittedtranstrack.trajectoryStateClosestToPoint(vtxXYZ);
    if(!postscp.isValid() or !negtscp.isValid()) return outputmap;
    GlobalVector positiveP(postscp.momentum());
    outputmap["pxpos"] = positiveP.x();
    outputmap["pypos"] = positiveP.y();
    outputmap["pzpos"] = positiveP.z();
    outputmap["ptpos"] = positiveP.transverse();
    outputmap["etapos"] = positiveP.eta();
    outputmap["phipos"] = positiveP.phi();
    GlobalVector negativeP(negtscp.momentum());
    outputmap["pxneg"] = negativeP.x();
    outputmap["pyneg"] = negativeP.y();
    outputmap["pzneg"] = negativeP.z();
    outputmap["ptneg"] = negativeP.transverse();
    outputmap["etaneg"] = negativeP.eta();
    outputmap["phineg"] = negativeP.phi();
    GlobalVector totalP(positiveP + negativeP);
    outputmap["px"] = totalP.x();
    outputmap["py"] = totalP.y();
    outputmap["pz"] = totalP.z();
    outputmap["pt"] = totalP.transverse();
    outputmap["eta"] = totalP.eta();
    outputmap["phi"] = totalP.phi();

    // (optional) condition: cosine of pointing angle must be close to one (not default)
    // note: now commented out since it can be easily recalculated and used in selections
    //       in downstream stages of the analysis.
    /*double px = totalP.x(); double py = totalP.y();
    double x = v0vtx.position().x()-primaryVertexXYZ.x();
    double y = v0vtx.position().y()-primaryVertexXYZ.y();
    double cospointing_pv = (x*px+y*py)/(sqrt(pow(x,2)+pow(y,2))*sqrt(pow(px,2)+pow(py,2)));
    x = v0vtx.position().x()-beamSpotXYZ.x();
    y = v0vtx.position().y()-beamSpotXYZ.y();
    double cospointing_bs = (x*px+y*py)/(sqrt(pow(x,2)+pow(y,2))*sqrt(pow(px,2)+pow(py,2)));
    if(cospointing_pv<0.99 and cospointing_bs<0.99) return outputmap; // good value: 0.99 (trial and error) */

    // calculate energy assuming Kshort, Lambda and LambdaBar
    double piPlusE = sqrt(positiveP.mag2() + pimass2); // pi plus
    double piMinE = sqrt(negativeP.mag2() + pimass2); // pi minus
    double pE = sqrt(positiveP.mag2() + pmass2); // proton
    double pBarE = sqrt(negativeP.mag2() + pmass2); // antiproton
    double KsETot = piPlusE + piMinE;
    double LambdaETot = pE + piMinE;
    double LambdaBarETot = pBarE + piPlusE;
    // calculate corresponding mass
    math::XYZTLorentzVector KsP4(totalP.x(),totalP.y(),totalP.z(),KsETot);
    double KsInvMass = KsP4.M();
    math::XYZTLorentzVector LambdaP4(totalP.x(),totalP.y(),totalP.z(),LambdaETot);
    double LambdaInvMass = LambdaP4.M();
    math::XYZTLorentzVector LambdaBarP4(totalP.x(),totalP.y(),totalP.z(),LambdaBarETot);
    double LambdaBarInvMass = LambdaBarP4.M();
    // mass must be close to Ks mass (default 0.07) or Lambda mass (default 0.05)
    if(std::abs(KsInvMass-ksmass) > 0.07 and std::abs(LambdaInvMass-lambdamass) > 0.05
		and std::abs(LambdaBarInvMass-lambdamass) > 0.05) return outputmap;

    // fill track properties
    outputmap["nhitspos"] = postrack.numberOfValidHits();
    outputmap["nhitsneg"] = negtrack.numberOfValidHits();
    outputmap["normchi2pos"] = postrack.normalizedChi2();
    outputmap["normchi2neg"] = negtrack.normalizedChi2();
    reco::TrackBase::Point refPoint(primaryVertex.position().x(),
					primaryVertex.position().y(),
					primaryVertex.position().z());
    outputmap["d0pos"] = postrack.dxy(refPoint);
    outputmap["dzpos"] = postrack.dz(refPoint);
    outputmap["d0neg"] = negtrack.dxy(refPoint);
    outputmap["dzneg"] = negtrack.dz(refPoint);
    outputmap["isopos"] = getTrackRelIso(postrack,iEvent);
    outputmap["isoneg"] = getTrackRelIso(negtrack,iEvent);

    // case 1: V0hort
    if(std::abs(KsInvMass-ksmass) < 0.07 
		and std::abs(KsInvMass-ksmass)<std::abs(LambdaInvMass-lambdamass)
		and std::abs(KsInvMass-ksmass)<std::abs(LambdaBarInvMass-lambdamass)){
        outputmap["invmass"] = KsInvMass;
	outputmap["type"] = 1.;
        return outputmap;
    }
    // case 2a: mass close to Lambda mass (default: 0.05)
    if(std::abs(LambdaInvMass-lambdamass) < 0.05
		and std::abs(LambdaInvMass-lambdamass)<std::abs(KsInvMass-ksmass)
		and std::abs(LambdaInvMass-lambdamass)<std::abs(LambdaBarInvMass-lambdamass)){
        outputmap["invmass"] = LambdaInvMass;
	outputmap["type"] = 2.;
        return outputmap;
    }
    // case 2b: same but candidate is a LambdaBar
    if(std::abs(LambdaBarInvMass-lambdamass) < 0.05
		and std::abs(LambdaBarInvMass-lambdamass)<std::abs(KsInvMass-ksmass)
		and std::abs(LambdaBarInvMass-lambdamass)<std::abs(LambdaInvMass-lambdamass)){
        outputmap["invmass"] = LambdaBarInvMass;
	outputmap["type"] = 3.;
        return outputmap;
    }
    // if none of the above, return the (still invalid) outputmap
    return outputmap;
}
