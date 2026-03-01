from m5.objects import (
    System,
    SrcClockDomain,
    VoltageDomain,
    AddrRange,
    SystemXBar,
    DDR3_1600_8x8,
    MemCtrl,
    SEWorkload,
    Process,
    DerivO3CPU,
    Cache,
    Root,
)
import m5


class L1ICache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


class L1DCache(Cache):
    size = "32KiB"
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20


def build_system(width: int):
    system = System()

    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange("512MiB")]

    cpu = DerivO3CPU()

    cpu.decodeWidth = width
    cpu.renameWidth = width
    cpu.dispatchWidth = width
    cpu.issueWidth = width
    cpu.wbWidth = width
    cpu.commitWidth = width

    system.cpu = cpu

    system.cpu.icache = L1ICache()
    system.cpu.dcache = L1DCache()

    system.membus = SystemXBar()

    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    system.cpu.icache.mem_side = system.membus.cpu_side_ports
    system.cpu.dcache.mem_side = system.membus.cpu_side_ports

    system.cpu.createInterruptController()
    if hasattr(system.cpu, "interrupts"):
        system.cpu.interrupts[0].pio = system.membus.mem_side_ports
        system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
        system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    system.workload = SEWorkload.init_compatible("./tests/hello")
    process = Process()
    process.cmd = ["./tests/hello"]
    system.cpu.workload = process
    system.cpu.createThreads()

    return system


if __name__ == "__m5_main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--width",
        type=int,
        default=2,
        help=(
            "Pipeline width (decode/issue/commit) for DerivO3CPU."
        ),
    )
    args, unknown = parser.parse_known_args()

    if args.width < 2:
        raise ValueError(
            "This DerivO3CPU configuration does not safely support a width"
        )

    system = build_system(width=args.width)
    root = Root(full_system=False, system=system)
    m5.instantiate()

    print(f"Beginning DerivO3CPU simulation with width={args.width}")
    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

