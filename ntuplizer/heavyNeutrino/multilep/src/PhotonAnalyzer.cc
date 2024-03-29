#include "heavyNeutrino/multilep/interface/PhotonAnalyzer.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "heavyNeutrino/multilep/interface/GenTools.h"
/*
 * Calculating all photon-related variables
 */


PhotonAnalyzer::PhotonAnalyzer(const edm::ParameterSet& iConfig, multilep* multilepAnalyzer):
    chargedEffectiveAreas((iConfig.getParameter<edm::FileInPath>("photonsChargedEffectiveAreas")).fullPath()),
    neutralEffectiveAreas((iConfig.getParameter<edm::FileInPath>("photonsNeutralEffectiveAreas")).fullPath()),
    photonsEffectiveAreas((iConfig.getParameter<edm::FileInPath>("photonsPhotonsEffectiveAreas")).fullPath()),
    multilepAnalyzer(multilepAnalyzer)
{};


void PhotonAnalyzer::beginJob(TTree* outputTree){
    outputTree->Branch("_nPh",                                &_nPh,                            "_nPh/i");
    outputTree->Branch("_phPt",                               &_phPt,                           "_phPt[_nPh]/D");
    outputTree->Branch("_phEta",                              &_phEta,                          "_phEta[_nPh]/D");
    outputTree->Branch("_phEtaSC",                            &_phEtaSC,                        "_phEtaSC[_nPh]/D");
    outputTree->Branch("_phPhi",                              &_phPhi,                          "_phPhi[_nPh]/D");
    outputTree->Branch("_phE",                                &_phE,                            "_phE[_nPh]/D");
    outputTree->Branch("_phCutBasedLoose",                    &_phCutBasedLoose,                "_phCutBasedLoose[_nPh]/O");
    outputTree->Branch("_phCutBasedMedium",                   &_phCutBasedMedium,               "_phCutBasedMedium[_nPh]/O");
    outputTree->Branch("_phCutBasedTight",                    &_phCutBasedTight,                "_phCutBasedTight[_nPh]/O");
    outputTree->Branch("_phMvaS16v1",                         &_phMvaS16v1,                     "_phMvaS16v1[_nPh]/D");
    outputTree->Branch("_phMvaF17v1p1",                       &_phMvaF17v1p1,                   "_phMvaF17v1p1[_nPh]/D");
    outputTree->Branch("_phMvaF17v2",                         &_phMvaF17v2,                     "_phMvaF17v2[_nPh]/D");
    outputTree->Branch("_phRandomConeChargedIsolation",       &_phRandomConeChargedIsolation,   "_phRandomConeChargedIsolation[_nPh]/D");
    // outputTree->Branch("_phChargedIsolation",                 &_phChargedIsolation,             "_phChargedIsolation[_nPh]/D");
    // outputTree->Branch("_phNeutralHadronIsolation",           &_phNeutralHadronIsolation,       "_phNeutralHadronIsolation[_nPh]/D");

    outputTree->Branch("_rhoCorrCharged",                     &_rhoCorrCharged,                 "_rhoCorrCharged[_nPh]/D");
    outputTree->Branch("_rhoCorrNeutral",                     &_rhoCorrNeutral,                 "_rhoCorrNeutral[_nPh]/D");
    outputTree->Branch("_rhoCorrPhotons",                     &_rhoCorrPhotons,                 "_rhoCorrPhotons[_nPh]/D");
    outputTree->Branch("_puChargedHadronIso",                 &_puChargedHadronIso,             "_puChargedHadronIso[_nPh]/D");
    // outputTree->Branch("_phoWorstChargedIsolation",           &_phoWorstChargedIsolation,       "_phoWorstChargedIsolation[_nPh]/D");

    // outputTree->Branch("_phPhotonIsolation",                  &_phPhotonIsolation,              "_phPhotonIsolation[_nPh]/D");
    outputTree->Branch("_phSigmaIetaIeta",                    &_phSigmaIetaIeta,                "_phSigmaIetaIeta[_nPh]/D");
    outputTree->Branch("_phHadronicOverEm",                   &_phHadronicOverEm,               "_phHadronicOverEm[_nPh]/D");
    outputTree->Branch("_phHadTowOverEm",                     &_phHadTowOverEm,                 "_phHadTowOverEm[_nPh]/D");
    outputTree->Branch("_phPassElectronVeto",                 &_phPassElectronVeto,             "_phPassElectronVeto[_nPh]/O");
    outputTree->Branch("_phHasPixelSeed",                     &_phHasPixelSeed,                 "_phHasPixelSeed[_nPh]/O");
    if( multilepAnalyzer->isMC() ){
      outputTree->Branch("_phIsPrompt",                       &_phIsPrompt,                     "_phIsPrompt[_nPh]/O");
      outputTree->Branch("_phTTGMatchCategory",               &_phTTGMatchCategory,             "_phTTGMatchCategory[_nPh]/I");
      outputTree->Branch("_phTTGMatchPt",                     &_phTTGMatchPt,                   "_phTTGMatchPt[_nPh]/D");
      outputTree->Branch("_phTTGMatchEta",                    &_phTTGMatchEta,                  "_phTTGMatchEta[_nPh]/D");
      outputTree->Branch("_phMatchPdgId",                     &_phMatchPdgId,                   "_phMatchPdgId[_nPh]/I");
    }
    outputTree->Branch("_phPtCorr",                           &_phPtCorr,                       "_phPtCorr[_nPh]/D");
    outputTree->Branch("_phPtScaleUp",                        &_phPtScaleUp,                    "_phPtScaleUp[_nPh]/D");
    outputTree->Branch("_phPtScaleDown",                      &_phPtScaleDown,                  "_phPtScaleDown[_nPh]/D");
    outputTree->Branch("_phPtResUp",                          &_phPtResUp,                      "_phPtResUp[_nPh]/D");
    outputTree->Branch("_phPtResDown",                        &_phPtResDown,                    "_phPtResDown[_nPh]/D");
    outputTree->Branch("_phECorr",                            &_phECorr,                        "_phECorr[_nPh]/D");
    outputTree->Branch("_phEScaleUp",                         &_phEScaleUp,                     "_phEScaleUp[_nPh]/D");
    outputTree->Branch("_phEScaleDown",                       &_phEScaleDown,                   "_phEScaleDown[_nPh]/D");
    outputTree->Branch("_phEResUp",                           &_phEResUp,                       "_phEResUp[_nPh]/D");
    outputTree->Branch("_phEResDown",                         &_phEResDown,                     "_phEResDown[_nPh]/D");

    generator = TRandom3(0);
}


bool PhotonAnalyzer::analyze(const edm::Event& iEvent){
    edm::Handle<std::vector<pat::Photon>> photons              = getHandle(iEvent, multilepAnalyzer->photonToken);
    edm::Handle<std::vector<pat::PackedCandidate>> packedCands = getHandle(iEvent, multilepAnalyzer->packedCandidatesToken);
    edm::Handle<std::vector<reco::Vertex>> vertices            = getHandle(iEvent, multilepAnalyzer->vtxToken);
    edm::Handle<std::vector<pat::Electron>> electrons          = getHandle(iEvent, multilepAnalyzer->eleToken);
    edm::Handle<std::vector<pat::Muon>> muons                  = getHandle(iEvent, multilepAnalyzer->muonToken);
    edm::Handle<std::vector<pat::Jet>> jets                    = getHandle(iEvent, multilepAnalyzer->jetToken);
    edm::Handle<std::vector<reco::GenParticle>> genParticles   = getHandle(iEvent, multilepAnalyzer->genParticleToken);
    edm::Handle<double> rho                                    = getHandle(iEvent, multilepAnalyzer->rhoToken);

    // Loop over photons
    _nPh = 0;
    for(auto photon = photons->begin(); photon != photons->end(); ++photon){
        if(_nPh == nPhoton_max) break;
        const auto photonRef = edm::Ref<std::vector<pat::Photon>>(photons, (photon - photons->begin()));

        if(photon->pt()  < 10)        continue;
        if(fabs(photon->eta()) > 2.5) continue;
        _rhoCorrCharged[_nPh] = (*rho)*chargedEffectiveAreas.getEffectiveArea(photon->superCluster()->eta());
        _rhoCorrNeutral[_nPh] = (*rho)*neutralEffectiveAreas.getEffectiveArea(photon->superCluster()->eta());
        _rhoCorrPhotons[_nPh] = (*rho)*photonsEffectiveAreas.getEffectiveArea(photon->superCluster()->eta());
        double randomConeIsoUnCorr = randomConeIso(photon->superCluster()->eta(), packedCands, *(vertices->begin()), electrons, muons, jets, photons);

        _phPt[_nPh]                         = photon->pt();
        _phEta[_nPh]                        = photon->eta();
        _phEtaSC[_nPh]                      = photon->superCluster()->eta();
        _phPhi[_nPh]                        = photon->phi();
        _phE[_nPh]                          = photon->energy();
        _phCutBasedLoose[_nPh]              = photon->photonID("cutBasedPhotonID-Fall17-94X-V2-loose");
        _phCutBasedMedium[_nPh]             = photon->photonID("cutBasedPhotonID-Fall17-94X-V2-medium");
        _phCutBasedTight[_nPh]              = photon->photonID("cutBasedPhotonID-Fall17-94X-V2-tight");
        _phMvaS16v1[_nPh]                   = photon->userFloat("PhotonMVAEstimatorRun2Spring16NonTrigV1Values");
        _phMvaF17v1p1[_nPh]                 = photon->userFloat("PhotonMVAEstimatorRunIIFall17v1p1Values");
        _phMvaF17v2[_nPh]                   = photon->userFloat("PhotonMVAEstimatorRunIIFall17v2Values");

        _phRandomConeChargedIsolation[_nPh] = randomConeIsoUnCorr < 0 ? -1 : std::max(0., randomConeIsoUnCorr - _rhoCorrCharged[_nPh]); // keep -1 when randomConeIso algorithm failed
        // _phChargedIsolation[_nPh]           = std::max(0., photon->userFloat("phoChargedIsolation") - _rhoCorrCharged[_nPh]);
        // _phNeutralHadronIsolation[_nPh]     = std::max(0., photon->userFloat("phoNeutralHadronIsolation") - _rhoCorrNeutral[_nPh]);
        // _phPhotonIsolation[_nPh]            = std::max(0., photon->userFloat("phoPhotonIsolation") - _rhoCorrPhotons[_nPh]);
        _puChargedHadronIso[_nPh]           = photon->userIsolation(pat::PfPUChargedHadronIso);
        // _phoWorstChargedIsolation[_nPh]     = photon->userFloat("phoWorstChargedIsolation");

        _phSigmaIetaIeta[_nPh]              = photon->full5x5_sigmaIetaIeta();
        _phHadronicOverEm[_nPh]             = photon->hadronicOverEm();
        _phHadTowOverEm[_nPh]               = photon->hadTowOverEm();
        _phPassElectronVeto[_nPh]           = photon->passElectronVeto();
        _phHasPixelSeed[_nPh]               = photon->hasPixelSeed();

        // Note: for the scale and smearing systematics we use the overall values, assuming we are not very sensitive to these systematics
        // In case these systematics turn out to be important, need to add their individual source to the tree (and propagate to their own templates):
        // https://twiki.cern.ch/twiki/bin/viewauth/CMS/EgammaMiniAODV2#Energy_Scale_and_Smearing
        _phPtCorr[_nPh]                     = photon->pt()*photon->userFloat("ecalEnergyPostCorr")/photon->energy();
        _phPtScaleUp[_nPh]                  = photon->pt()*photon->userFloat("energyScaleUp")/photon->energy();
        _phPtScaleDown[_nPh]                = photon->pt()*photon->userFloat("energyScaleDown")/photon->energy();
        _phPtResUp[_nPh]                    = photon->pt()*photon->userFloat("energySigmaUp")/photon->energy();
        _phPtResDown[_nPh]                  = photon->pt()*photon->userFloat("energySigmaDown")/photon->energy();
        _phECorr[_nPh]                      = photon->userFloat("ecalEnergyPostCorr");
        _phEScaleUp[_nPh]                   = photon->userFloat("energyScaleUp");
        _phEScaleDown[_nPh]                 = photon->userFloat("energyScaleDown");
        _phEResUp[_nPh]                     = photon->userFloat("energySigmaUp");
        _phEResDown[_nPh]                   = photon->userFloat("energySigmaDown");

        if( multilepAnalyzer->isMC() ){
            fillPhotonGenVars(photon->genParticle());
            matchCategory(*photon, genParticles);
        }
        ++_nPh;
    }

    if(multilepAnalyzer->skim == "singlephoton" and _nPh < 1) return false;
    if(multilepAnalyzer->skim == "diphoton" and _nPh < 2) return false;
    return true;
}

void PhotonAnalyzer::fillPhotonGenVars(const reco::GenParticle* genParticle){
    if(genParticle != nullptr){
        _phIsPrompt[_nPh]   = (genParticle)->isPromptFinalState();
        _phMatchPdgId[_nPh] = (genParticle)->pdgId();
    } else{
        _phIsPrompt[_nPh]   = false;
        _phMatchPdgId[_nPh] = 0;
    }
}



double PhotonAnalyzer::randomConeIso(double eta, edm::Handle<std::vector<pat::PackedCandidate>>& pfcands, const reco::Vertex& vertex,
        edm::Handle<std::vector<pat::Electron>>& electrons, edm::Handle<std::vector<pat::Muon>>& muons,
        edm::Handle<std::vector<pat::Jet>>& jets, edm::Handle<std::vector<pat::Photon>>& photons){

    // First, find random phi direction which does not overlap with jets, photons or leptons
    bool overlap   = true;
    int attempt    = 0;
    double randomPhi;
    while(overlap and attempt<20){
        randomPhi = generator.Uniform(-TMath::Pi(),TMath::Pi());

        overlap = false;
        for(auto& p : *electrons) if(p.pt() > 10 and deltaR(eta, randomPhi, p.eta(), p.phi()) < 0.6) overlap = true;
        for(auto& p : *muons)     if(p.pt() > 10 and deltaR(eta, randomPhi, p.eta(), p.phi()) < 0.6) overlap = true;
        for(auto& p : *jets)      if(p.pt() > 20 and deltaR(eta, randomPhi, p.eta(), p.phi()) < 0.6) overlap = true;
        for(auto& p : *photons)   if(p.pt() > 10 and deltaR(eta, randomPhi, p.eta(), p.phi()) < 0.6) overlap = true;
        ++attempt;
    }
    if(overlap) return -1.;

    // Calculate chargedIsolation
    float chargedIsoSum = 0;
    for(auto& iCand : *pfcands){
        if(iCand.hasTrackDetails()){
            if(deltaR(eta, randomPhi, iCand.eta(), iCand.phi()) > 0.3) continue;
            if(abs(iCand.pdgId()) != 211) continue;

            float dxy = iCand.pseudoTrack().dxy(vertex.position());
            float dz  = iCand.pseudoTrack().dz(vertex.position());
            if(fabs(dxy) > 0.1) continue;
            if(fabs(dz) > 0.2)  continue;

            chargedIsoSum += iCand.pt();
        }
    }
    return chargedIsoSum;
}


void PhotonAnalyzer::matchCategory(const pat::Photon& photon, edm::Handle<std::vector<reco::GenParticle>>& genParticles){
    enum matchCategory {UNDEFINED, GENUINE, MISIDELE, HADRONICPHOTON, HADRONICFAKE, MAGIC, UNMHADRONICPHOTON, UNMHADRONICFAKE};
    _phTTGMatchCategory[_nPh] = UNDEFINED;
    _phTTGMatchPt[_nPh]       = -1.;
    _phTTGMatchEta[_nPh]      = -10.;

    float minDeltaR = 999;
    const reco::GenParticle* matched = nullptr;

    for(auto& p : *genParticles){
      // if(p.status()!=1 and p.status()!=71)  continue;
      if(p.status()!=1)  continue;
      if(fabs(p.pt()-photon.pt())/p.pt() > 0.5) continue;
      float myDeltaR = deltaR(p.eta(), p.phi(), photon.eta(), photon.phi());
      if(myDeltaR > 0.3 or myDeltaR > minDeltaR) continue;
      minDeltaR  = myDeltaR;
      matched    = &p;
    }

    if(matched){
      _phTTGMatchPt[_nPh]  = matched->pt();
      _phTTGMatchEta[_nPh] = matched->eta();
      bool noMesonsInChain   = GenTools::noMesonsInChain(*matched, *genParticles);
      if(matched->pdgId() == 22){
        if(noMesonsInChain)                                   _phTTGMatchCategory[_nPh] = GENUINE;
        else                                                  _phTTGMatchCategory[_nPh] = HADRONICPHOTON;
      }
        else if(abs(matched->pdgId())==11)                    _phTTGMatchCategory[_nPh] = MISIDELE;
        else                                                  _phTTGMatchCategory[_nPh] = HADRONICFAKE;
    } else{
        bool anyNear= false;
        for(auto& p : *genParticles){
          if(not(p.pdgId() > 0)) continue;
          if(p.pt() < 5.) continue;
          if(abs(p.pdgId()) == 12 or abs(p.pdgId()) == 14 or abs(p.pdgId()) == 16) continue;
          float myDeltaR = deltaR(p.eta(), p.phi(), photon.eta(), photon.phi());
          if(myDeltaR > 0.3) continue;
          anyNear = true;
        }
        if(GenTools::phoAndPiNear(photon, *genParticles))     _phTTGMatchCategory[_nPh] = UNMHADRONICPHOTON;
        else if(not anyNear)                                  _phTTGMatchCategory[_nPh] = MAGIC;
        else                                                  _phTTGMatchCategory[_nPh] = UNMHADRONICFAKE;
    }
}
