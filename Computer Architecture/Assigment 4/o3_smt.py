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


def build_system(num_threads: int):
    system = System()

    system.clk_domain = SrcClockDomain()
    system.clk_domain.clock = "1GHz"
    system.clk_domain.voltage_domain = VoltageDomain()

    system.mem_mode = "timing"
    system.mem_ranges = [AddrRange("512MiB")]

    cpu = DerivO3CPU()
    cpu.numThreads = num_threads
    system.cpu = cpu

    system.multi_thread = num_threads > 1

    system.cpu.icache = L1ICache()
    system.cpu.dcache = L1DCache()

    system.membus = SystemXBar()

    system.cpu.icache.cpu_side = system.cpu.icache_port
    system.cpu.dcache.cpu_side = system.cpu.dcache_port

    system.cpu.icache.mem_side = system.membus.cpu_side_ports
    system.cpu.dcache.mem_side = system.membus.cpu_side_ports

    system.cpu.createInterruptController()
    if hasattr(system.cpu, "interrupts"):
        for thread_id in range(num_threads):
            system.cpu.interrupts[thread_id].pio = system.membus.mem_side_ports
            system.cpu.interrupts[thread_id].int_requestor = system.membus.cpu_side_ports
            system.cpu.interrupts[thread_id].int_responder = system.membus.mem_side_ports

    system.mem_ctrl = MemCtrl()
    system.mem_ctrl.dram = DDR3_1600_8x8()
    system.mem_ctrl.dram.range = system.mem_ranges[0]
    system.mem_ctrl.port = system.membus.mem_side_ports

    # Set up a system-call emulation workload compatible with the binary.
    system.workload = SEWorkload.init_compatible("./tests/hello")

    processes = []
    for thread_id in range(num_threads):
        proc = Process()
        proc.pid = 100 + thread_id  # ensure unique process identifiers
        proc.cmd = ["./tests/hello"]
        processes.append(proc)

    if num_threads == 1:
        system.cpu.workload = processes[0]
    else:
        system.cpu.workload = processes

    system.cpu.createThreads()

    return system


if __name__ == "__m5_main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num-threads",
        type=int,
        default=2,
        help="Number of hardware threads for SMT (1 = no SMT).",
    )
    args, unknown = parser.parse_known_args()

    system = build_system(num_threads=args.num_threads)
    root = m5.objects.Root(full_system=False, system=system)
    m5.instantiate()

    print(f"Beginning DerivO3CPU SMT simulation with numThreads={args.num_threads}")
    exit_event = m5.simulate()
    print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")

