#!/usr/bin/env python3

"""
BEAST XML template string
"""
beast_template = """
<beast version="2.6" namespace="beast.core:beast.evolution.alignment:beast.evolution.tree.coalescent:beast.core.util:beast.evolution.nuc:beast.evolution.operators:beast.evolution.sitemodel:beast.evolution.substitutionmodel:beast.evolution.likelihood">
    <data spec="Alignment" dataType="standard" statecount={nsymbols} id="alignment">
        <!-- Start sequences -->
        <!-- End sequences -->
        <userDataType spec="beast.evolution.datatype.StandardData">
            <!-- Start charstatelabels -->
            <!-- End charstatelabels -->
        </userDataType>
    </data>
    <map name="Uniform">beast.math.distributions.Uniform</map>
    <map name="Exponential">beast.math.distributions.Exponential</map>
    <map name="LogNormal">beast.math.distributions.LogNormalDistributionModel</map>
    <map name="Normal">beast.math.distributions.Normal</map>
    <map name="Beta">beast.math.distributions.Beta</map>
    <map name="Gamma">beast.math.distributions.Gamma</map>
    <map name="LaplaceDistribution">beast.math.distributions.LaplaceDistribution</map>
    <map name="prior">beast.math.distributions.Prior</map>
    <map name="InverseGamma">beast.math.distributions.InverseGamma</map>
    <map name="OneOnX">beast.math.distributions.OneOnX</map>
    <!-- The chainLength attribute should be increased to a large number (e.g., 20000000) for non-test runs -->
    <run spec="MCMC" id="mcmc" chainLength="100000">
        <state spec="State" id="state" storeEvery="5000">
            <tree spec="beast.evolution.tree.Tree" id="tree">
                <trait spec="beast.evolution.tree.TraitSet" traitname="date" units="year" value="{date_map}">
                    <taxa spec="TaxonSet" alignment="@alignment"/>
                </trait>
            </tree>
            <parameter spec="parameter.RealParameter" id="becomeUninfectiousRate_BDSKY_Serial.t:alignment" lower="0.0" name="stateNode" upper="Infinity">1.0</parameter>
            <parameter spec="parameter.RealParameter" id="reproductiveNumber_BDSKY_Serial.t:alignment" dimension="10" lower="0.0" name="stateNode" upper="Infinity">2.0</parameter>
            <parameter spec="parameter.RealParameter" id="samplingProportion_BDSKY_Serial.t:alignment" lower="0.0" name="stateNode" upper="1.0">0.01</parameter>
            <parameter spec="parameter.RealParameter" id="ucldMean.c:alignment" name="stateNode">1.0</parameter>
            <parameter spec="parameter.RealParameter" id="ucldStdevParameter" lower="0.0" name="stateNode" estimate="false">0.000001</parameter>
            <stateNode spec="parameter.IntegerParameter" id="rateCategories.c:alignment" dimension="74">1</stateNode>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockScaleFactor" name="stateNode" lower="0.0" upper="10.0">1</parameter>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactor" name="stateNode">500</parameter>
            <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddle" name="stateNode">600</parameter>
            <!-- Start transcriptional parameters -->
            <!-- End transcriptional parameters -->
            <!-- We include a "default" rate fixed at 1 that corresponds to (unlikely) transitions with no transcriptional explanation.
            All other rates in the substitution matrices will be estimated relative to this.
            If no other transcriptional rate parameters are specified, then the substitution matrices will correspond to those of the Lewis Mk model. -->
            <parameter spec="parameter.RealParameter" id="default_rate" name="stateNode" estimate="false">1.0</parameter>
        </state>
        <init spec="beast.evolution.tree.RandomTree" id="RandomTree.t:alignment" estimate="false" initial="@tree" taxa="@alignment">
            <populationModel spec="ConstantPopulation" id="ConstantPopulation0.t:alignment">
                <parameter spec="parameter.RealParameter" id="randomPopSize.t:alignment" name="popSize">1.0</parameter>
            </populationModel>
        </init>
        <distribution spec="util.CompoundDistribution" id="posterior">
            <distribution spec="util.CompoundDistribution" id="prior">
                <distribution spec="beast.evolution.speciation.BirthDeathSkylineModel" id="BDSKY_Serial.t:alignment" becomeUninfectiousRate="@becomeUninfectiousRate_BDSKY_Serial.t:alignment" reproductiveNumber="@reproductiveNumber_BDSKY_Serial.t:alignment" samplingProportion="@samplingProportion_BDSKY_Serial.t:alignment" tree="@tree">
                    <parameter spec="parameter.RealParameter" id="origin_BDSKY_Serial.t:alignment" estimate="false" lower="1250.0" name="origin" upper="1250.0">1250.0</parameter>
                </distribution>
                <prior id="becomeUninfectiousRatePrior_BDSKY_Serial.t:alignment" name="distribution" x="@becomeUninfectiousRate_BDSKY_Serial.t:alignment">
                    <LogNormal id="LogNormalDistributionModel.1" name="distr">
                    <parameter spec="parameter.RealParameter" id="RealParameter.13" estimate="false" name="M">0.0</parameter>
                    <parameter spec="parameter.RealParameter" id="RealParameter.14" estimate="false" name="S">1.0</parameter>
                    </LogNormal>
                </prior>
                <prior id="reproductiveNumberPrior_BDSKY_Serial.t:alignment" name="distribution" x="@reproductiveNumber_BDSKY_Serial.t:alignment">
                    <LogNormal id="LogNormalDistributionModel.2" name="distr">
                    <parameter spec="parameter.RealParameter" id="RealParameter.15" estimate="false" name="M">0.0</parameter>
                    <parameter spec="parameter.RealParameter" id="RealParameter.16" estimate="false" name="S">1.0</parameter>
                    </LogNormal>
                </prior>
                <prior id="samplingProportionPrior_BDSKY_Serial.t:alignment" name="distribution" x="@samplingProportion_BDSKY_Serial.t:alignment">
                    <Beta id="Beta.1" name="distr">
                        <parameter spec="parameter.RealParameter" id="RealParameter.17" estimate="false" name="alpha">1.0</parameter>
                        <parameter spec="parameter.RealParameter" id="RealParameter.18" estimate="false" name="beta">1.0</parameter>
                    </Beta>
                </prior>
                <prior id="MeanRatePrior.c:alignment" name="distribution" x="@ucldMean.c:alignment">
                    <Uniform id="Uniform.4" name="distr" upper="Infinity"/>
                </prior>
                <prior id="nonhomogeneousClockScaleFactorPrior" name="distribution" x="@nonhomogeneousClockScaleFactor">
                    <!--
                    <Uniform id="nonhomogeneousClockScaleFactorPriorDistribution" name="distr" lower="0.0" upper="20.0"/>
                    -->
                    <Exponential id="nonhomogeneousClockScaleFactorPriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockScaleFactorPriorDistributionMean" estimate="false" name="mean">1.0</parameter>
                    </Exponential>
                </prior>
                <prior id="nonhomogeneousClockGrowthFactorPrior" name="distribution" x="@nonhomogeneousClockGrowthFactor">
                    <!--
                    <Uniform id="nonhomogeneousClockGrowthFactorPriorDistribution" name="distr" lower="1" upper="1000.0"/>
                    -->
                    <Normal id="nonhomogeneousClockGrowthFactorPriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactorPriorDistributionMean" estimate="false" name="mean">500.0</parameter>
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockGrowthFactorPriorDistributionSigma" estimate="false" name="sigma">500.0</parameter>
                    </Normal>
                </prior>
                <prior id="nonhomogeneousClockMiddlePrior" name="distribution" x="@nonhomogeneousClockMiddle">
                    <!--
                    <Uniform id="nonhomogeneousClockMiddlePriorDistribution" name="distr" lower="0" upper="1250.0"/>
                    -->
                    <Normal id="nonhomogeneousClockMiddlePriorDistribution" name="distr">
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddlePriorDistributionMean" estimate="false" name="mean">500.0</parameter>
                        <parameter spec="parameter.RealParameter" id="nonhomogeneousClockMiddlePriorDistributionSigma" estimate="false" name="sigma">500.0</parameter>
                    </Normal>
                </prior>
            </distribution>
            <distribution spec="util.CompoundDistribution" id="likelihood" useThreads="true">
                <!-- Start character distributions -->
                <!-- End character distributions -->
            </distribution>
        </distribution>
        <operator spec="ScaleOperator" id="BDSKY_SerialTreeScaler.t:alignment" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="BDSKY_SerialTreeRootScaler.t:alignment" rootOnly="true" scaleFactor="0.5" tree="@tree" weight="3.0"/>
        <operator spec="Uniform" id="BDSKY_SerialUniformOperator.t:alignment" tree="@tree" weight="30.0"/>
        <operator spec="SubtreeSlide" id="BDSKY_SerialSubtreeSlide.t:alignment" tree="@tree" weight="15.0"/>
        <operator spec="Exchange" id="BDSKY_SerialNarrow.t:alignment" tree="@tree" weight="0.0"/>
        <operator spec="Exchange" id="BDSKY_SerialWide.t:alignment" isNarrow="false" tree="@tree" weight="3.0"/>
        <operator spec="WilsonBalding" id="BDSKY_SerialWilsonBalding.t:alignment" tree="@tree" weight="3.0"/>
        <operator spec="ScaleOperator" id="becomeUninfectiousRateScaler_BDSKY_Serial.t:alignment" parameter="@becomeUninfectiousRate_BDSKY_Serial.t:alignment" weight="2.0"/>
        <operator spec="ScaleOperator" id="reproductiveNumberScaler_BDSKY_Serial.t:alignment" parameter="@reproductiveNumber_BDSKY_Serial.t:alignment" weight="10.0"/>
        <operator spec="ScaleOperator" id="samplingProportionScaler_BDSKY_Serial.t:alignment" parameter="@samplingProportion_BDSKY_Serial.t:alignment" weight="10.0"/>
        <operator spec="UpDownOperator" id="updownBD_BDSKY_Serial.t:alignment" scaleFactor="0.75" weight="2.0">
            <up idref="reproductiveNumber_BDSKY_Serial.t:alignment"/>
            <down idref="becomeUninfectiousRate_BDSKY_Serial.t:alignment"/>
        </operator>
        <operator spec="ScaleOperator" id="ucldMeanScaler.c:alignment" parameter="@ucldMean.c:alignment" scaleFactor="0.5" weight="1.0"/>
        <operator spec="IntRandomWalkOperator" id="CategoriesRandomWalk.c:alignment" parameter="@rateCategories.c:alignment" weight="10.0" windowSize="1"/>
        <operator spec="SwapOperator" id="CategoriesSwapOperator.c:alignment" intparameter="@rateCategories.c:alignment" weight="10.0"/>
        <operator spec="UniformOperator" id="CategoriesUniform.c:alignment" parameter="@rateCategories.c:alignment" weight="10.0"/>
        <operator spec="UpDownOperator" id="relaxedUpDownOperator.c:alignment" scaleFactor="0.75" weight="3.0">
            <up idref="ucldMean.c:alignment"/>
            <down idref="Tree.t:alignment"/>
        </operator>
        <operator spec="ScaleOperator" id="nonhomogeneousClockScaleFactorOperator" parameter="@nonhomogeneousClockScaleFactor" weight="1.0"/>
        <operator spec="ScaleOperator" id="nonhomogeneousClockGrowthFactorOperator" parameter="@nonhomogeneousClockGrowthFactor" weight="1.0"/>
        <operator spec="ScaleOperator" id="nonhomogeneousClockMiddleOperator" parameter="@nonhomogeneousClockMiddle" weight="1.0"/>
        <!-- Start transcriptional operators -->
        <!-- End transcriptional operators -->
        <logger spec="Logger" id="tracelog" fileName="beast.log" logEvery="1000" model="@posterior" sanitiseHeaders="true" sort="smart">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
            <log spec="beast.evolution.tree.TreeHeightLogger" id="TreeHeight.t:alignment" tree="@tree"/>
            <log idref="BDSKY_Serial.t:alignment"/>
            <log idref="becomeUninfectiousRate_BDSKY_Serial.t:alignment"/>
            <log idref="reproductiveNumber_BDSKY_Serial.t:alignment"/>
            <log idref="samplingProportion_BDSKY_Serial.t:alignment"/>
            <log idref="ucldMean.c:alignment"/>
            <log idref="ucldStdevParameter"/>
            <log spec="beast.evolution.branchratemodel.RateStatistic" id="rate.c:alignment" branchratemodel="@RelaxedClock.c:alignment" tree="@tree"/>
            <log idref="nonhomogeneousClockScaleFactor"/>
            <log idref="nonhomogeneousClockGrowthFactor"/>
            <log idref="nonhomogeneousClockMiddle"/>
            <!-- Start transcriptional loggers -->
            <!-- End transcriptional loggers -->
        </logger>
        <logger spec="Logger" id="screenlog" logEvery="1000">
            <log idref="posterior"/>
            <log idref="likelihood"/>
            <log idref="prior"/>
        </logger>
        <logger spec="Logger" id="treelog.t:alignment" fileName="$(tree).trees" logEvery="1000" mode="tree">
            <log spec="beast.evolution.tree.TreeWithMetaDataLogger" id="TreeWithMetaDataLogger.t:alignment" branchratemodel="@RelaxedClock.c:alignment" tree="@tree"/>
        </logger>
        <operatorschedule spec="OperatorSchedule" id="OperatorSchedule"/>
        <logger id="AncestralSequenceLogger" fileName="$(tree).ancestral.trees" logEvery="10000" mode="tree">
            <!-- Start character ancestral state loggers -->
            <!-- End character ancestral state loggers -->
        </logger>
    </run>
</beast>
"""

"""
BEAST XML sequence template string
"""
sequence_template = """
<sequence spec="Sequence" taxon="{wit_id}" uncertain="true" value="{sequence}"/>
"""

"""
BEAST XML charstatelabels template string
"""
charstatelabels_template = """
<charstatelabels spec="beast.evolution.datatype.UserDataType" characterName="{vu_id}" codeMap="{code_map}" states="{nstates}" value="{rdg_texts}"/>
"""

"""
BEAST XML transcriptional rate parameter template string
"""
parameter_template = """
<parameter spec="parameter.RealParameter" id="{rate_id}_rate" name="stateNode" lower="1.0" upper="Infinity" estimate="true">1.0</parameter>
"""

"""
BEAST XML distribution template string
"""
distribution_template = """
<distribution id="morphTreeLikelihood.character{vu_ind}" useAmbiguities="true" useTipLikelihoods="true" spec="TreeLikelihood" tree="@tree">
    <data spec="FilteredAlignment" id="filter1" data="@alignment" filter="{vu_ind}">
        <userDataType spec="beast.evolution.datatype.StandardData" id="morphDataType.character{vu_ind}" ambiguities="" nrOfStates="{nstates}"/>
    </data>
    <siteModel spec="SiteModel" id="morphSiteModel.character{vu_ind}">
        <parameter spec="parameter.RealParameter" id="mutationRate.character{vu_ind}" estimate="false" name="mutationRate">1.0</parameter>
        <parameter spec="parameter.RealParameter" id="gammaShape.character{vu_ind}" estimate="false" name="shape">1.0</parameter>
        <substModel spec="GeneralSubstitutionModel" id="SubstModel.character{vu_ind}">
            <!-- Equilibrium state frequencies -->
            <frequencies spec="Frequencies" id="freqs.character{vu_ind}">
                <!-- Start equilibrium frequencies -->
                <!-- End equilibrium frequencies -->
            </frequencies>
            <parameter spec="parameter.CompoundValuable" id="rates.character{vu_ind}" name="rates">
                <!-- Start rate vars -->
                <!-- End rate vars -->
            </parameter>
        </substModel>
    </siteModel>
    <rootFrequencies spec="Frequencies" id="rootfreqs.character{vu_ind}">
        <!-- Start root frequencies -->
        <!-- End root frequencies -->
    </rootFrequencies>
    <!-- Start branchRateModel -->
    <!-- End branchRateModel -->
</distribution>
"""

"""
BEAST XML frequencies template
"""
frequencies_template = """
<frequencies spec="parameter.RealParameter" id="frequencies.character{vu_ind}" value="{frequencies}" estimate="false"/>
"""

"""
BEAST XML branch rate model template for first site only
"""
first_branch_rate_model_template = """
<branchRateModel spec="beast.evolution.branchratemodel.NonHomogeneousClockModel" id="RelaxedClock.c:alignment" clock.rate="@ucldMean.c:alignment" rateCategories="@rateCategories.c:alignment" tree="@tree" scaleFactor="@nonhomogeneousClockScaleFactor" growthFactor="@nonhomogeneousClockGrowthFactor" middle="@nonhomogeneousClockMiddle">
    <LogNormal id="LogNormalDistributionModel.c:alignment" S="@ucldStdevParameter" meanInRealSpace="true" name="distr">
        <parameter spec="parameter.RealParameter" id="RealParameter.23" estimate="false" lower="0.0" name="M" upper="1.0">1.0</parameter>
    </LogNormal>
</branchRateModel>
"""

"""
BEAST XML branch rate model template for sites after the first
"""
other_branch_rate_model_template = """
<branchRateModel idref="RelaxedClock.c:alignment"/>
"""

"""
BEAST XML single rate variable template
"""
single_var_template = """
<var idref="{rate_id}_rate"/>
"""

"""
BEAST XML multiple rate variable template (rate parameters being added should be appended as child var elements)
"""
multiple_var_template = """
<var spec="beast.core.util.Sum"/>
"""
