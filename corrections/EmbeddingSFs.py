# Author: Izaak Neutelings (December 2018)
# /shome/ytakahas/work/Leptoquark/CMSSW_9_4_4/src/PhysicsTools/NanoAODTools/NanoTreeProducer/leptonSF
# HTT: https://github.com/CMS-HTT/LeptonEfficiencies
# https://twiki.cern.ch/twiki/bin/view/CMS/MuonReferenceEffs2017
from corrections import modulepath
from ScaleFactorTool import ScaleFactor, ScaleFactorHTT, ScaleFactorEmb


class EmbeddingSFs:
    def __init__(self, year=2017):
        """Load histograms from files."""

        assert year in [
            2016, 2017, 2018
        ], "EmbeddingSFs: You must choose a year from: 2016, 2017, or 2018."
        if year == 2016:
            pathEmb = modulepath + "/leptonEfficiencies/kit/inputs/2018/KIT/v18_2/"
            self.sftool_trig = ScaleFactorEmb(
                pathEmb + "Muon_Run2016_legacy_IsoMu22.root", 'ZMass',
                'mu_trig')
            self.sftool_idiso = ScaleFactorEmb(
                pathEmb + "Muon_Run2016_legacy_IdIso.root", 'ZMass',
                'mu_idiso')
            self.sftool_seltrig = ScaleFactorEmb(
                pathEmb + "Muon_Run2016_DoubleMuon.root", 'ZMass',
                'emb_sel_trig')
        elif year == 2017:
            pathEmb = modulepath + "/leptonEfficiencies/kit/inputs/2017/KIT/legacy/"
            pathEmbSel = modulepath + "/leptonEfficiencies/kit/inputs/2017/ICSF/2017/"
            self.sftool_id = ScaleFactorEmb(
                pathEmb + "muon_TP_Data_2017_Fits_ID_pt_eta_bins.root",
                pathEmb + "muon_TP_Embedding_2017_Fits_ID_pt_eta_bins.root",
                'ID',2017)  # MediumID,
            self.sftool_iso = ScaleFactorEmb(
                pathEmb + "muon_TP_Data_2017_Fits_Iso_pt_eta_bins.root",
                pathEmb + "muon_TP_Embedding_2017_Fits_Iso_pt_eta_bins.root",
                "Iso",2017)  # isolation
            self.sftool_trig = ScaleFactorEmb(
                pathEmb +
                "muon_TP_Data_2017_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root",
                pathEmb +
                "muon_TP_Embedding_2017_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root",
                'Trg_IsoMu27_or_IsoMu24',2017)
            self.sftool_seltrig = ScaleFactorEmb(
                pathEmbSel + "Mu8/muon_SFs.root",
                pathEmbSel + "Mu17/muon_SFs.root",
                'selection',2017)
        else:
            pathEmb = modulepath + "/leptonEfficiencies/kit/inputs/2018/KIT/v18_2/"
            pathEmbSel = modulepath + "/leptonEfficiencies/kit/inputs/2018/KIT/2018/"
            self.sftool_id = ScaleFactorEmb(
                pathEmb + "muon_TP_Data_2018_Fits_ID_pt_eta_bins.root",
                pathEmb + "muon_TP_Embedding_2018_Fits_ID_pt_eta_bins.root",
                'ID',2018)  # MediumID,
            self.sftool_iso = ScaleFactorEmb(
                pathEmb + "muon_TP_Data_2018_Fits_Iso_pt_eta_bins.root",
                pathEmb + "muon_TP_Embedding_2018_Fits_Iso_pt_eta_bins.root",
                "Iso",2018)  # isolation
            self.sftool_trig = ScaleFactorEmb(
                pathEmb +
                "muon_TP_Data_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root",
                pathEmb +
                "muon_TP_Embedding_2018_Fits_Trg_IsoMu27_or_IsoMu24_pt_eta_bins.root",
                'Trg_IsoMu27_or_IsoMu24',2018)
            self.sftool_seltrig = ScaleFactorEmb(
                pathEmbSel + "Mu8/muon_SFs.root",
                pathEmbSel + "Mu17/muon_SFs.root", 'selection',2018)

    def getTriggerSF(self, pt, eta):
        """Get SF for single muon trigger."""
        return self.sftool_trig.getSF(pt, abs(eta))

    def getIsoSF(self, pt, eta):
        """Get SF for muon Isolation."""
        return self.sftool_trig.getSF(pt, abs(eta))

    def getIdSF(self, pt, eta):
        """Get SF for muon identification """
        return self.sftool_id.getSF(pt, abs(eta))

    def getEmbSelSF(self, pt_1, eta_1, pt_2, eta_2):
        """ Get SF for Embeddeded DoubleMuon Selection """
        return self.sftool_seltrig.getSelectionSF(pt_1, abs(eta_1), pt_2,
                                                  abs(eta_2))
